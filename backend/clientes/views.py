"""
Vistas del modulo CLIENTES.

CRUD completo, restringido al rol Administrador: la informacion de
los clientes es sensible y no debe ser visible para otros clientes.
"""

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from bookspace_manager.vistas import EliminacionProtegidaMixin
from clientes.forms import ClienteForm
from clientes.models import Cliente
from cuentas.mixins import AdministradorRequeridoMixin


class ClienteListView(AdministradorRequeridoMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        registros = Cliente.objects.annotate(
            total_reservas=Count('reservas_del_cliente')
        ).order_by('apellidos', 'nombres')
        consulta = self.request.GET.get('q', '').strip()
        if consulta:
            registros = registros.filter(
                Q(nombres__icontains=consulta)
                | Q(apellidos__icontains=consulta)
                | Q(cedula__icontains=consulta)
                | Q(correo__icontains=consulta)
            )
        return registros


class ClienteDetailView(AdministradorRequeridoMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['reservas'] = self.object.reservas_del_cliente.select_related(
            'espacio'
        )[:10]
        return contexto


class ClienteCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:lista')
    success_message = 'Cliente registrado correctamente.'


class ClienteUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:lista')
    success_message = 'Cliente actualizado correctamente.'


class ClienteDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:lista')
    context_object_name = 'cliente'
    mensaje_protegido = (
        'No se puede eliminar el cliente: tiene reservas registradas. '
        'Puedes marcarlo como inactivo.'
    )
