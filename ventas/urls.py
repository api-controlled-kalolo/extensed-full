from django.urls import path
from ventas import views

app_name = 'ventas'

urlpatterns = [
    path('acta/create/', views.create_acta, name = 'acta_create'),
    path('ventas/', views.ventas_modulo, name = 'modulo_ventas' ),
    path('acta/gestion', views.gestion_actas, name = 'actas_gestion')
]