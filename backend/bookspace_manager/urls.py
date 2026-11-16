"""
URL configuration for bookspace_manager project.

Cada modulo (app) publica sus propias rutas y aqui se integran
al enrutador principal del proyecto mediante include().
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    path('', include('panel.urls')),
    path('cuentas/', include('cuentas.urls')),
    path('espacios/', include('espacios.urls')),
    path('clientes/', include('clientes.urls')),
    path('reservas/', include('reservas.urls')),
    path('pagos/', include('pagos.urls')),
    path('cafeteria/', include('cafeteria.urls')),
    path('libreria/', include('libreria.urls')),
]

admin.site.site_header = 'Raccoon Café - Administración'
admin.site.site_title = 'Raccoon Café'
admin.site.index_title = 'Panel de administracion'
