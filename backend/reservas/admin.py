"""Registro de los modelos de RESERVAS en el administrador de Django."""

from django.contrib import admin

from reservas.models import DetalleReserva, Reserva


class DetalleReservaInline(admin.TabularInline):
    model = DetalleReserva
    extra = 0
    readonly_fields = ['precio_unitario', 'subtotal']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'codigo',
        'cliente',
        'espacio',
        'fecha',
        'hora_inicio',
        'hora_fin',
        'estado',
        'total',
    ]
    list_filter = ['estado', 'fecha', 'espacio']
    search_fields = ['codigo', 'cliente__nombres', 'cliente__apellidos']
    date_hierarchy = 'fecha'
    readonly_fields = [
        'codigo',
        'subtotal_espacio',
        'subtotal_servicios',
        'total',
        'fecha_registro',
    ]
    inlines = [DetalleReservaInline]


@admin.register(DetalleReserva)
class DetalleReservaAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'servicio', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['servicio']
    readonly_fields = ['precio_unitario', 'subtotal']
