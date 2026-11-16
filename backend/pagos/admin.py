"""Registro de los modelos de PAGOS en el administrador de Django."""

from django.contrib import admin

from pagos.models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'monto', 'metodo_pago', 'estado', 'fecha_pago']
    list_filter = ['metodo_pago', 'estado']
    search_fields = ['reserva__codigo', 'referencia']
    readonly_fields = ['fecha_pago']
    date_hierarchy = 'fecha_pago'
