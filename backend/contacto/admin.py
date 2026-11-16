"""Registro de los mensajes de contacto en el administrador de Django."""

from django.contrib import admin

from contacto.models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'correo', 'asunto', 'leido', 'creado_en']
    list_editable = ['leido']
    list_filter = ['leido', 'asunto']
    search_fields = ['nombre', 'correo', 'mensaje']
    readonly_fields = ['creado_en']
    list_per_page = 25
