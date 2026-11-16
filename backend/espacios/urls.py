"""Rutas del modulo ESPACIOS."""

from django.urls import path

from espacios import views

app_name = 'espacios'

urlpatterns = [
    # --- Tipos de espacio ---
    path('tipos/', views.TipoEspacioListView.as_view(), name='tipo_lista'),
    path('tipos/nuevo/', views.TipoEspacioCreateView.as_view(), name='tipo_crear'),
    path('tipos/<int:pk>/', views.TipoEspacioDetailView.as_view(), name='tipo_detalle'),
    path('tipos/<int:pk>/editar/', views.TipoEspacioUpdateView.as_view(), name='tipo_editar'),
    path('tipos/<int:pk>/eliminar/', views.TipoEspacioDeleteView.as_view(), name='tipo_eliminar'),

    # --- Espacios ---
    path('', views.EspacioListView.as_view(), name='espacio_lista'),
    path('nuevo/', views.EspacioCreateView.as_view(), name='espacio_crear'),
    path('<int:pk>/', views.EspacioDetailView.as_view(), name='espacio_detalle'),
    path('<int:pk>/editar/', views.EspacioUpdateView.as_view(), name='espacio_editar'),
    path('<int:pk>/eliminar/', views.EspacioDeleteView.as_view(), name='espacio_eliminar'),

    # --- Servicios adicionales ---
    path('servicios/', views.ServicioListView.as_view(), name='servicio_lista'),
    path('servicios/nuevo/', views.ServicioCreateView.as_view(), name='servicio_crear'),
    path('servicios/<int:pk>/', views.ServicioDetailView.as_view(), name='servicio_detalle'),
    path('servicios/<int:pk>/editar/', views.ServicioUpdateView.as_view(), name='servicio_editar'),
    path('servicios/<int:pk>/eliminar/', views.ServicioDeleteView.as_view(), name='servicio_eliminar'),
]
