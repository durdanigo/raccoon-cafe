"""Rutas del modulo CUENTAS."""

from django.urls import path

from cuentas import views

app_name = 'cuentas'

urlpatterns = [
    path('login/', views.IniciarSesionView.as_view(), name='login'),
    path('logout/', views.CerrarSesionView.as_view(), name='logout'),
    path('registro/', views.RegistroClienteView.as_view(), name='registro'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
