"""
Vistas del modulo CONTACTO.

Bandeja de entrada de los mensajes del formulario publico. Es de uso
interno: solo el rol Administrador puede verla, marcar mensajes como
leidos o eliminarlos.
"""

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DeleteView, ListView

from contacto.models import Mensaje
from cuentas.mixins import AdministradorRequeridoMixin


class MensajeListView(AdministradorRequeridoMixin, ListView):
    model = Mensaje
    template_name = 'contacto/mensaje_list.html'
    context_object_name = 'mensajes'
    paginate_by = 10

    def get_queryset(self):
        registros = Mensaje.objects.all()
        estado = self.request.GET.get('estado', '').strip()
        asunto = self.request.GET.get('asunto', '').strip()
        if estado == 'pendientes':
            registros = registros.filter(leido=False)
        elif estado == 'leidos':
            registros = registros.filter(leido=True)
        if asunto in Mensaje.Asunto.values:
            registros = registros.filter(asunto=asunto)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['asuntos'] = Mensaje.Asunto.choices
        contexto['pendientes'] = Mensaje.objects.filter(leido=False).count()
        return contexto


class MensajeAlternarLeidoView(AdministradorRequeridoMixin, View):
    """Cambia un mensaje entre leido y pendiente (solo por POST)."""

    http_method_names = ['post']

    def post(self, request, pk):
        mensaje = get_object_or_404(Mensaje, pk=pk)
        mensaje.leido = not mensaje.leido
        mensaje.save(update_fields=['leido'])
        messages.success(
            request,
            'Mensaje marcado como leido.' if mensaje.leido else 'Mensaje marcado como pendiente.',
        )
        # Solo se vuelve a rutas del propio sitio (evita redirecciones abiertas).
        siguiente = request.POST.get('siguiente', '')
        if url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
            return redirect(siguiente)
        return redirect('contacto:lista')


class MensajeDeleteView(AdministradorRequeridoMixin, SuccessMessageMixin, DeleteView):
    model = Mensaje
    template_name = 'contacto/mensaje_confirm_delete.html'
    success_url = reverse_lazy('contacto:lista')
    context_object_name = 'mensaje'
    success_message = 'Mensaje eliminado correctamente.'
