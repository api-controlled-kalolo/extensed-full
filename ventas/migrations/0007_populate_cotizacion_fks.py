from django.db import migrations


def forwards(apps, schema_editor):
    Proyecto = apps.get_model('ventas', 'Proyecto')
    Cliente = apps.get_model('ventas', 'Cliente')
    Contacto = apps.get_model('ventas', 'Contacto')
    Cotizacion = apps.get_model('ventas', 'Cotizacion')

    proj, _ = Proyecto.objects.get_or_create(codigo='P-DEFAULT', defaults={'nombre': 'Default'})

    for cot in Cotizacion.objects.filter(cliente__isnull=True):
        # Determinar RUC y nombre
        ruc_val = (cot.dato_ruc or cot.ruc or f"RUC-{cot.pk}").strip()
        nombre_cliente = (cot.dato_empresa or cot.razon_social or f"Cliente {cot.pk}").strip()
        cliente_codigo = f"C-{cot.pk}"

        # Truncar valores a los tamaños máximos declarados en los modelos
        # Cliente.codigo -> max_length=20, Cliente.ruc -> 20, Cliente.razon_social -> 20, direccion -> 50
        ruc_val = ruc_val[:20]
        nombre_cliente = nombre_cliente[:20]
        cliente_codigo = cliente_codigo[:20]

        # Crear o reutilizar cliente por RUC (ruc es único en el modelo)
        cliente, created = Cliente.objects.get_or_create(
            ruc=ruc_val,
            defaults={
                'codigo': cliente_codigo,
                'razon_social': nombre_cliente,
                'direccion': cot.direccion or '',
                'distrito': 'N/A',
                'provincia': 'N/A',
                'proyecto_principal': proj,
            }
        )

        # Crear un contacto único por cotización para evitar colisiones con unique=True
        contacto_apellidos = f"Contacto-{cot.pk}"[:20]
        contacto_nombres = f"Nombre-{cot.pk}"[:20]
        contacto_cargo = f"Cargo-{cot.pk}"[:20]
        contacto_sede = f"Sede-{cot.pk}"[:20]

        correo_val = (cot.contacto_correo or cot.correo or '')[:254]
        celular_val = (cot.contacto_celular or cot.celular or '')[:9]

        contacto, _ = Contacto.objects.get_or_create(
            cliente_principal=cliente,
            apellidos=contacto_apellidos,
            nombres=contacto_nombres,
            defaults={
                'cargo': contacto_cargo,
                'correo': correo_val,
                'Celular': celular_val,
                'Sede': contacto_sede,
            }
        )

        cot.cliente = cliente
        cot.contacto = contacto
        cot.save(update_fields=['cliente', 'contacto'])


def reverse(apps, schema_editor):
    # No revertimos automáticamente los cambios de datos
    return


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0006_cliente_proyecto_unidadnegocio_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
