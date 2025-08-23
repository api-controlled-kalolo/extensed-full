from django.urls import path
from ventas import views

app_name = 'ventas'

urlpatterns = [
    path('acta/create/', views.create_acta, name = 'acta_create')
]