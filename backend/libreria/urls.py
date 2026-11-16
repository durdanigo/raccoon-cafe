"""Rutas del modulo LIBRERIA."""

from django.urls import path

from libreria import views

app_name = 'libreria'

urlpatterns = [
    path('', views.LibroListView.as_view(), name='libro_lista'),
    path('nuevo/', views.LibroCreateView.as_view(), name='libro_crear'),
    path('<int:pk>/editar/', views.LibroUpdateView.as_view(), name='libro_editar'),
    path('<int:pk>/eliminar/', views.LibroDeleteView.as_view(), name='libro_eliminar'),
]
