"""Rutas del modulo PAGOS."""

from django.urls import path

from pagos import views

app_name = 'pagos'

urlpatterns = [
    path('', views.PagoListView.as_view(), name='lista'),
    path('nuevo/', views.PagoCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.PagoDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.PagoUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.PagoDeleteView.as_view(), name='eliminar'),
]
