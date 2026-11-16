"""Rutas del modulo CAFETERIA."""

from django.urls import path

from cafeteria import views

app_name = 'cafeteria'

urlpatterns = [
    # --- Productos del menu ---
    path('', views.ProductoListView.as_view(), name='producto_lista'),
    path('nuevo/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_eliminar'),

    # --- Categorias ---
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),
]
