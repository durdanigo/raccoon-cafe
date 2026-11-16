"""Utilidades compartidas por las vistas del sistema."""

from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect


class EliminacionProtegidaMixin:
    """Evita el error 500 cuando un registro tiene dependencias.

    Todas las claves foraneas del sistema usan on_delete=PROTECT, por lo
    que Django lanza ProtectedError si el registro esta en uso. Este mixin
    captura ese error y muestra un mensaje entendible para el usuario.
    """

    mensaje_protegido = 'No se puede eliminar: el registro esta siendo usado en el sistema.'

    def form_valid(self, form):
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.mensaje_protegido)
            return redirect(self.get_success_url())
        messages.success(self.request, 'Registro eliminado correctamente.')
        return respuesta
