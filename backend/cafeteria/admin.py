"""Registro de los modelos de CAFETERIA en el administrador de Django."""

from django.contrib import admin

from cafeteria.models import CategoriaMenu, ProductoMenu


@admin.register(CategoriaMenu)
class CategoriaMenuAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'activa']
    list_editable = ['orden', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre']


@admin.register(ProductoMenu)
class ProductoMenuAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'categoria',
        'precio',
        'controla_stock',
        'stock',
        'stock_minimo',
        'disponible',
    ]
    list_editable = ['precio', 'stock', 'disponible']
    list_filter = ['categoria', 'disponible', 'controla_stock']
    search_fields = ['nombre', 'descripcion']
    list_per_page = 25
