"""Registro de los modelos de CLIENTES en el administrador de Django."""

from django.contrib import admin

from clientes.models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'cedula',
        'nombres',
        'apellidos',
        'correo',
        'telefono',
        'tipo_cliente',
        'activo',
    ]
    list_filter = ['tipo_cliente', 'activo']
    search_fields = ['cedula', 'nombres', 'apellidos', 'correo']
    ordering = ['apellidos', 'nombres']
    readonly_fields = ['fecha_registro']
