from django.urls import path
from ventas import views
# filepath: ventas/urls.py
from ventas.views import create_acta, gestion_actas, ventas_modulo, generar_cotizacion, menu_cotizaciones, crear_unidad_negocio, crear_proyecto, crear_cliente, crear_contacto, cotizaciones_dashboard, contactos_por_cliente_api, cambiar_estado_cotizacion, visualizar_pdf_cotizacion, detalle_cotizacion
from ventas.views.cliente import cliente_dashboard, listar_clientes, editar_cliente, eliminar_cliente, buscar_clientes_json
from ventas.views.contacto import contacto_dashboard, listar_contactos, editar_contacto, eliminar_contacto, buscar_contactos_json
from ventas.views.cotizaciones import obtener_datos_cliente_api, obtener_datos_contacto_api

app_name = 'ventas'

urlpatterns = [
    # -- MODULO: Ventas
    path('ventas/', ventas_modulo, name = 'modulo_ventas' ),
    
    # -- ACTAS
    path('acta/create/', create_acta, name = 'acta_create'),
    path('acta/gestion', gestion_actas, name = 'actas_gestion'),
    
    # -- COTIZACIONES
    path('cotizacion/create', generar_cotizacion, name='cotizacion_create'),
    path('cotizacion/gestion', menu_cotizaciones, name='cotizacion_gestion'),
    path('cotizaciones/', views.cotizaciones_list, name='cotizaciones_list'),
    path('cotizaciones/dashboard/', views.cotizaciones_dashboard, name='cotizaciones_dashboard'),
    path('cotizaciones/<int:pk>/cambiar-estado/', views.cambiar_estado_cotizacion, name='cambiar_estado_cotizacion'),
    path('cotizaciones/<int:pk>/pdf/', views.visualizar_pdf_cotizacion, name='visualizar_pdf_cotizacion'),
    path('cotizaciones/<int:pk>/detalle/', views.detalle_cotizacion, name='detalle_cotizacion'),
    
    # API: contactos por cliente
    path('api/clientes/<int:cliente_id>/contactos', contactos_por_cliente_api, name='api_contactos_por_cliente'),
    path('api/clientes/<int:cliente_id>/datos', obtener_datos_cliente_api, name='api_datos_cliente'),
    path('api/contactos/<int:contacto_id>/datos', obtener_datos_contacto_api, name='api_datos_contacto'),
    
    # -- UN
    path('unidadnegocio/create', crear_unidad_negocio, name='unidadnegocio'),
    
    # -- Proyecto
    path('proyecto/create', crear_proyecto, name='proyectocrear'),
    
    # -- Cliente
    path('clientes/', cliente_dashboard, name='cliente_dashboard'),
    path('clientes/create', crear_cliente, name='clientecrear'),
    path('clientes/listar/', listar_clientes, name='listar_clientes'),
    path('clientes/buscar/', buscar_clientes_json, name='buscar_clientes_json'),
    path('clientes/<int:cliente_id>/editar/', editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', eliminar_cliente, name='eliminar_cliente'),
    
    # -- Contacto
    path('contactos/', contacto_dashboard, name='contacto_dashboard'),
    path('contactos/create', crear_contacto, name='contactocrear'),
    path('contactos/listar/', listar_contactos, name='listar_contactos'),
    path('contactos/buscar/', buscar_contactos_json, name='buscar_contactos_json'),
    path('contactos/<int:contacto_id>/editar/', editar_contacto, name='editar_contacto'),
    path('contactos/<int:contacto_id>/eliminar/', eliminar_contacto, name='eliminar_contacto'),
]   