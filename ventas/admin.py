from django.contrib import admin
from .models import ActaServicioTecnico, Equipos_ActaServicioTecnico, Acciones_ActaServicioTecnico, UnidadNegocio, Proyecto, Cliente, Contacto, Cotizacion, Detalles_Cotizacion
# Register your models here.
admin.site.register(ActaServicioTecnico),
admin.site.register(Equipos_ActaServicioTecnico),
admin.site.register(Acciones_ActaServicioTecnico),
admin.site.register(UnidadNegocio),
admin.site.register(Proyecto),
admin.site.register(Cliente),
admin.site.register(Contacto),
admin.site.register(Cotizacion),
admin.site.register(Detalles_Cotizacion),