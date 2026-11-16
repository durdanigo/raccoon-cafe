"""Rutas del modulo PANEL."""

from django.urls import path

from panel import views

app_name = 'panel'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('calendario/', views.CalendarioView.as_view(), name='calendario'),
    path('api/eventos/', views.EventosCalendarioView.as_view(), name='api_eventos'),
]
