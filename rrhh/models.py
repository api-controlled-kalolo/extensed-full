from datetime import datetime

from django.db import models

from ventas.models import Proyecto
# Create your models here.
class Personal(models.Model):
    codigo= models.CharField(max_length=20, unique=True, null=False, help_text="Indentificador único para el personal")
    nombres = models.CharField(max_length=30, null=False, help_text="Nombres para el personal")
    apellidos = models.CharField(max_length=30, null=False, help_text="Apellidos para el personal")
    cargo = models.CharField(max_length=30, null=False, help_text="Cargo que usara el usuario")
    dni = models.CharField(max_length=8, null=False, unique=True, help_text="Ingese N° DNI")
    empresa_afp = models.CharField(max_length=30, null=False)
    numero_afp = models.CharField(max_length=20, null=False)
    fecha_ingreso = models.DateField(null=False)
    tipo_comision_afp = models.CharField(max_length=20, null=False)
    bono = models.CharField(max_length=20, null=False)
    activo = models.BooleanField(default=True)
    modalidad = models.CharField(max_length=20, null=False)
    domicilio = models.CharField(max_length=50,)
    inicio_de_contrato = models.DateField()
    vencimiento_contrato = models.DateField()
    contacto_emergencia = models.CharField(max_length=50, blank=True, null=True)
    num_emergencia = models.CharField(max_length=9)
    correo = models.EmailField()
    profesion = models.CharField(max_length=30)

    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='personal_asignado')
    
    def save(self, *args, **kwargs):
        # Generar número de cotización y datos de empresa
        if not self.pk and not self.codigo:
            super().save(*args, **kwargs)
            self.codigo = f"PER00{self.pk:02d}{datetime.now().year}"
            return super().save(update_fields=["codigo",])
        
        return super().save(*args, **kwargs)

class HijosPersonal(models.Model):
    id_personal = models.ForeignKey(Personal, on_delete= models.CASCADE, related_name="personal")
    
    nombre_hijo = models.CharField(max_length=50, blank=True, null=True)
    cumpleaños_hijo = models.DateField()