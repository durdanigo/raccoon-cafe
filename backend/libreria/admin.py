"""Registro de los modelos de LIBRERIA en el administrador de Django."""

from django.contrib import admin

from libreria.models import Libro


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = [
        'titulo',
        'autor',
        'tipo',
        'condicion',
        'precio',
        'stock',
        'estante',
        'disponible',
    ]
    list_editable = ['stock', 'disponible']
    list_filter = ['tipo', 'condicion', 'disponible', 'genero']
    search_fields = ['titulo', 'autor', 'genero']
    list_per_page = 25
