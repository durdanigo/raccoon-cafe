"""
Rutas de la API REST.

El enrutador de Django REST Framework genera automaticamente las rutas
de listado y detalle de cada conjunto de vistas:

    GET  /api/espacios/        listado
    GET  /api/espacios/<id>/   detalle
"""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views

app_name = 'api'

enrutador = SimpleRouter()
enrutador.register('tipos-espacio', views.TipoEspacioViewSet, basename='tipoespacio')
enrutador.register('espacios', views.EspacioViewSet, basename='espacio')
enrutador.register('servicios', views.ServicioViewSet, basename='servicio')
enrutador.register('clientes', views.ClienteViewSet, basename='cliente')
enrutador.register('reservas', views.ReservaViewSet, basename='reserva')
enrutador.register('pagos', views.PagoViewSet, basename='pago')
enrutador.register('categorias-menu', views.CategoriaMenuViewSet, basename='categoriamenu')
enrutador.register('menu', views.ProductoMenuViewSet, basename='productomenu')
enrutador.register('libros', views.LibroViewSet, basename='libro')
enrutador.register('contacto', views.MensajeViewSet, basename='mensaje')

urlpatterns = [
    path('', views.raiz_api, name='raiz'),
    path('', include(enrutador.urls)),
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
]
