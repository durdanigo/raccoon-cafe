"""Rutas del modulo CONTACTO."""

from django.urls import path

from contacto import views

app_name = 'contacto'

urlpatterns = [
    path('', views.MensajeListView.as_view(), name='lista'),
    path('<int:pk>/leido/', views.MensajeAlternarLeidoView.as_view(), name='alternar_leido'),
    path('<int:pk>/eliminar/', views.MensajeDeleteView.as_view(), name='eliminar'),
]
