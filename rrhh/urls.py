from django.urls import path

from . import views

app_name = "rrhh"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("personal/registrar/", views.personal_create, name="personal_create"),
    path("personal/", views.personal_list, name="personal_list"),
]
