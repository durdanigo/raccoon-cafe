"""Registro de los modelos de ESPACIOS en el administrador de Django."""

from django.contrib import admin

from espacios.models import Espacio, Servicio, TipoEspacio


@admin.register(TipoEspacio)
class TipoEspacioAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_espacio', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = [
        'codigo',
        'nombre',
        'tipo_espacio',
        'ubicacion',
        'capacidad',
        'tarifa_hora',
        'estado',
    ]
    list_filter = ['estado', 'tipo_espacio']
    search_fields = ['codigo', 'nombre', 'ubicacion']
    ordering = ['codigo']
    list_per_page = 20


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
