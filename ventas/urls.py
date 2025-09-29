from django.urls import path
from ventas import views
# filepath: ventas/urls.py
from ventas.views import create_acta, gestion_actas, ventas_modulo, generar_cotizacion, menu_cotizaciones, crear_unidad_negocio, crear_proyecto, crear_cliente, crear_contacto, cotizaciones_dashboard, contactos_por_cliente_api, cambiar_estado_cotizacion, visualizar_pdf_cotizacion, detalle_cotizacion

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
    
    # -- UN
    path('unidadnegocio/create', crear_unidad_negocio, name='unidadnegocio'),
    
    # -- Proyecto
    path('proyecto/create', crear_proyecto, name='proyectocrear'),
    
    # -- Cliente
    path('clientes/create', crear_cliente, name='clientecrear'),
    
    path('contactos/create', crear_contacto, name="contactocrear" )
]   