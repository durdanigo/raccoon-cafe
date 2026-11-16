"""
Vistas del modulo PAGOS.

CRUD completo de pagos. El cliente solo puede consultar los pagos de
sus propias reservas; el registro y la anulacion son del administrador.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from cuentas.mixins import AdministradorRequeridoMixin, cliente_de, es_administrador
from pagos.forms import PagoForm
from pagos.models import Pago
from reservas.models import Reserva


class FiltroPagosPorRolMixin(LoginRequiredMixin):
    def get_queryset(self):
        registros = Pago.objects.select_related('reserva', 'reserva__cliente')
        if not es_administrador(self.request.user):
            cliente = cliente_de(self.request.user)
            registros = (
                registros.filter(reserva__cliente=cliente) if cliente else registros.none()
            )
        return registros


class PagoListView(FiltroPagosPorRolMixin, ListView):
    model = Pago
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'
    paginate_by = 10

    def get_queryset(self):
        registros = super().get_queryset()
        consulta = self.request.GET.get('q', '').strip()
        metodo = self.request.GET.get('metodo', '').strip()
        if consulta:
            registros = registros.filter(
                Q(reserva__codigo__icontains=consulta)
                | Q(referencia__icontains=consulta)
                | Q(reserva__cliente__apellidos__icontains=consulta)
            )
        if metodo:
            registros = registros.filter(metodo_pago=metodo)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['metodos'] = Pago.MetodoPago.choices
        return contexto


class PagoDetailView(FiltroPagosPorRolMixin, DetailView):
    model = Pago
    template_name = 'pagos/pago_detail.html'
    context_object_name = 'pago'


class PagoCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:lista')
    success_message = 'Pago registrado correctamente.'

    def get_initial(self):
        inicial = super().get_initial()
        id_reserva = self.request.GET.get('reserva')
        if id_reserva:
            reserva = Reserva.objects.filter(pk=id_reserva).first()
            if reserva:
                inicial['reserva'] = reserva
                inicial['monto'] = reserva.saldo_pendiente
        return inicial

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)


class PagoUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:lista')
    success_message = 'Pago actualizado correctamente.'


class PagoDeleteView(AdministradorRequeridoMixin, DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pagos:lista')
    context_object_name = 'pago'
