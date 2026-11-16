"""Rutas del modulo RESERVAS."""

from django.urls import path

from reservas import views

app_name = 'reservas'

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='lista'),
    path('nueva/', views.ReservaCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.ReservaDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.ReservaUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.ReservaDeleteView.as_view(), name='eliminar'),
    path(
        '<int:pk>/estado/<str:estado>/',
        views.ReservaCambiarEstadoView.as_view(),
        name='cambiar_estado',
    ),

    # --- Servicios adicionales de la reserva ---
    path(
        '<int:pk>/servicios/agregar/',
        views.DetalleReservaCreateView.as_view(),
        name='detalle_agregar',
    ),
    path(
        'servicios/<int:pk>/eliminar/',
        views.DetalleReservaDeleteView.as_view(),
        name='detalle_eliminar',
    ),
]
