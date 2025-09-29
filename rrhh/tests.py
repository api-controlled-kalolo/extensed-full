from django.test import TestCase
from django.urls import reverse

from ventas.models import Proyecto, UnidadNegocio


class PersonalCreateViewTests(TestCase):
	def setUp(self):
		unidad = UnidadNegocio.objects.create(codigo="UNTEST", nombre="Unidad Test")
		self.proyecto = Proyecto.objects.create(
			codigo="PRTEST",
			nombre="Proyecto Test",
			unidad_negocio_principal=unidad
		)

	def test_get_personal_create_view(self):
		response = self.client.get(reverse("rrhh:personal_create"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Registrar nuevo personal")

	def test_get_dashboard_view(self):
		response = self.client.get(reverse("rrhh:dashboard"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Acciones rápidas de Recursos Humanos")

	def test_get_personal_list_view(self):
		response = self.client.get(reverse("rrhh:personal_list"))
		self.assertEqual(response.status_code, 200)
		self.assertIn("personal_list", response.context)
