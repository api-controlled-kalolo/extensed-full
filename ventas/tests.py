from django.test import TestCase
from django.urls import reverse

from ventas.models import Cliente, Proyecto, UnidadNegocio
from ventas.utils import ubigeo


class UbigeoUtilsTests(TestCase):
	def test_province_choices_available(self):
		provinces = ubigeo.get_province_choices()
		self.assertGreater(len(provinces), 0, "Se esperaba al menos una provincia disponible")

	def test_district_choices_are_linked(self):
		province_value, _ = ubigeo.get_province_choices()[0]
		districts = ubigeo.get_district_choices(province_value)
		self.assertGreater(len(districts), 0, "La provincia seleccionada debe tener distritos")
		district_value, _ = districts[0]
		self.assertTrue(
			ubigeo.ensure_district_matches_province(province_value, district_value),
			"El distrito debe pertenecer a la provincia",
		)


class UbigeoApiTests(TestCase):
	def test_districts_endpoint_returns_data(self):
		province_value, _ = ubigeo.get_province_choices()[0]
		response = self.client.get(reverse('ventas:ubigeo_distritos'), {'provincia': province_value})
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertIn('distritos', payload)
		self.assertGreater(len(payload['distritos']), 0)

	def test_districts_endpoint_handles_invalid_province(self):
		response = self.client.get(reverse('ventas:ubigeo_distritos'), {'provincia': 'invalida'})
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload, {'distritos': []})


class UnidadNegocioViewsTests(TestCase):
	def setUp(self):
		self.un = UnidadNegocio.objects.create(nombre='Infraestructura')

	def test_listado_unidades_responde(self):
		response = self.client.get(reverse('ventas:unidadnegocio_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Infraestructura')

	def test_creacion_unidad_redirige_al_listado(self):
		response = self.client.post(reverse('ventas:unidadnegocio'), {'nombre': 'Servicios Cloud'})
		self.assertRedirects(response, reverse('ventas:unidadnegocio_list'))
		self.assertTrue(UnidadNegocio.objects.filter(nombre='Servicios Cloud').exists())

	def test_nombre_duplicado_muestra_error(self):
		response = self.client.post(reverse('ventas:unidadnegocio'), {'nombre': 'Infraestructura'})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Ya existe una Unidad de Negocio')

	def test_eliminar_bloqueado_con_proyectos(self):
		Proyecto.objects.create(nombre='Proyecto 1', unidad_negocio_principal=self.un)
		response = self.client.post(reverse('ventas:unidadnegocio_eliminar', args=[self.un.pk]))
		self.assertRedirects(response, reverse('ventas:unidadnegocio_list'))
		self.assertTrue(UnidadNegocio.objects.filter(pk=self.un.pk).exists())


class ProyectoViewsTests(TestCase):
	def setUp(self):
		self.un = UnidadNegocio.objects.create(nombre='Operaciones')

	def test_codigo_generado_automaticamente(self):
		proyecto = Proyecto.objects.create(nombre='Proyecto A', unidad_negocio_principal=self.un)
		self.assertTrue(proyecto.codigo.startswith('P-'))
		self.assertEqual(len(proyecto.codigo), 5)  # P-###

	def test_listado_proyectos_responde(self):
		Proyecto.objects.create(nombre='Proyecto List', unidad_negocio_principal=self.un)
		response = self.client.get(reverse('ventas:proyecto_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Proyecto List')

	def test_creacion_proyecto_redirige_al_listado(self):
		response = self.client.post(reverse('ventas:proyectocrear'), {
			'nombre': 'Proyecto Nuevo',
			'unidad_negocio_principal': self.un.pk,
		})
		self.assertRedirects(response, reverse('ventas:proyecto_list'))
		self.assertTrue(Proyecto.objects.filter(nombre='Proyecto Nuevo').exists())

	def test_nombre_duplicado_en_misma_un(self):
		Proyecto.objects.create(nombre='Proyecto Duplicado', unidad_negocio_principal=self.un)
		response = self.client.post(reverse('ventas:proyectocrear'), {
			'nombre': 'Proyecto Duplicado',
			'unidad_negocio_principal': self.un.pk,
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Ya existe un proyecto con este nombre')

	def test_eliminar_bloqueado_con_clientes(self):
		proyecto = Proyecto.objects.create(nombre='Proyecto Clientes', unidad_negocio_principal=self.un)
		Cliente.objects.create(
			proyecto_principal=proyecto,
			ruc='12345678901',
			razon_social='Cliente Test',
			direccion='Dirección 123',
			distrito='Lima',
			provincia='Lima',
		)
		response = self.client.post(reverse('ventas:proyecto_eliminar', args=[proyecto.pk]))
		self.assertRedirects(response, reverse('ventas:proyecto_list'))
		self.assertTrue(Proyecto.objects.filter(pk=proyecto.pk).exists())

	def test_eliminar_sin_clientes(self):
		proyecto = Proyecto.objects.create(nombre='Proyecto Vacío', unidad_negocio_principal=self.un)
		response = self.client.post(reverse('ventas:proyecto_eliminar', args=[proyecto.pk]))
		self.assertRedirects(response, reverse('ventas:proyecto_list'))
		self.assertFalse(Proyecto.objects.filter(pk=proyecto.pk).exists())
