from django.urls import path
from login import views

app_name = 'login'

urlpatterns = [
    path('', views.sign_in, name="signin"),
    path('login/', views.sign_in, name="signin"),
    path('home/', views.home, name="home")
]