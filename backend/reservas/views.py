"""
Vistas del modulo RESERVAS.

CRUD completo de reservas mas la gestion de los servicios adicionales
(detalle de la reserva).

Control de acceso:
    - Administrador: ve y gestiona todas las reservas.
    - Cliente      : solo ve, crea y edita las reservas propias.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from cuentas.mixins import AdministradorRequeridoMixin, cliente_de, es_administrador
from reservas.forms import DetalleReservaForm, ReservaForm
from reservas.models import DetalleReserva, Reserva


class FiltroPorRolMixin(LoginRequiredMixin):
    """Limita el queryset a las reservas del cliente cuando no es admin."""

    def get_queryset(self):
        registros = Reserva.objects.select_related(
            'cliente', 'espacio', 'espacio__tipo_espacio'
        )
        if not es_administrador(self.request.user):
            cliente = cliente_de(self.request.user)
            registros = registros.filter(cliente=cliente) if cliente else registros.none()
        return registros


# ============================================================
# CRUD DE RESERVA
# ============================================================
class ReservaListView(FiltroPorRolMixin, ListView):
    model = Reserva
    template_name = 'reservas/reserva_list.html'
    context_object_name = 'reservas'
    paginate_by = 10

    def get_queryset(self):
        registros = super().get_queryset()
        consulta = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        if consulta:
            registros = registros.filter(
                Q(codigo__icontains=consulta)
                | Q(cliente__nombres__icontains=consulta)
                | Q(cliente__apellidos__icontains=consulta)
                | Q(espacio__codigo__icontains=consulta)
            )
        if estado:
            registros = registros.filter(estado=estado)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['estados'] = Reserva.Estado.choices
        return contexto


class ReservaDetailView(FiltroPorRolMixin, DetailView):
    model = Reserva
    template_name = 'reservas/reserva_detail.html'
    context_object_name = 'reserva'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['detalles'] = self.object.detalles_de_reserva.select_related('servicio')
        contexto['pagos'] = self.object.pagos_de_reserva.all()
        contexto['form_detalle'] = DetalleReservaForm(reserva=self.object)
        return contexto


class ReservaFormularioMixin:
    """Comparte la configuracion del formulario entre crear y editar."""

    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['es_administrador'] = es_administrador(self.request.user)
        kwargs['cliente_actual'] = cliente_de(self.request.user)
        return kwargs

    def form_valid(self, form):
        if not es_administrador(self.request.user):
            cliente = cliente_de(self.request.user)
            if cliente is None:
                messages.error(
                    self.request,
                    'Tu usuario no tiene un perfil de cliente asociado.',
                )
                return redirect('panel:dashboard')
            form.instance.cliente = cliente
        if not form.instance.registrada_por_id:
            form.instance.registrada_por = self.request.user
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        # El codigo no es un campo editable del formulario, por eso se
        # toma del objeto ya guardado.
        return self.success_message % {'codigo': self.object.codigo}

    def get_success_url(self):
        return reverse('reservas:detalle', args=[self.object.pk])


class ReservaCreateView(
    LoginRequiredMixin, ReservaFormularioMixin, SuccessMessageMixin, CreateView
):
    success_message = 'Reserva %(codigo)s registrada correctamente.'


class ReservaUpdateView(
    FiltroPorRolMixin, ReservaFormularioMixin, SuccessMessageMixin, UpdateView
):
    success_message = 'Reserva %(codigo)s actualizada correctamente.'


class ReservaDeleteView(FiltroPorRolMixin, DeleteView):
    model = Reserva
    template_name = 'reservas/reserva_confirm_delete.html'
    success_url = reverse_lazy('reservas:lista')
    context_object_name = 'reserva'

    def form_valid(self, form):
        if self.object.pagos_de_reserva.exists():
            messages.error(
                self.request,
                'No se puede eliminar la reserva: tiene pagos registrados. '
                'Cancelala en su lugar.',
            )
            return redirect('reservas:detalle', pk=self.object.pk)
        messages.success(self.request, 'Reserva eliminada correctamente.')
        return super().form_valid(form)


# ============================================================
# CAMBIO DE ESTADO DE LA RESERVA
# ============================================================
class ReservaCambiarEstadoView(AdministradorRequeridoMixin, View):
    """Confirma, cancela o completa una reserva desde su detalle."""

    def post(self, request, pk, estado):
        reserva = get_object_or_404(Reserva, pk=pk)
        estados_validos = dict(Reserva.Estado.choices)
        if estado not in estados_validos:
            messages.error(request, 'Estado no valido.')
            return redirect('reservas:detalle', pk=pk)

        if estado == Reserva.Estado.CONFIRMADA and reserva.saldo_pendiente > 0:
            messages.warning(
                request,
                f'La reserva se confirmo, pero mantiene un saldo pendiente de '
                f'${reserva.saldo_pendiente}.',
            )

        reserva.estado = estado
        reserva.save()
        messages.success(
            request, f'La reserva {reserva.codigo} ahora esta {estados_validos[estado]}.'
        )
        return redirect('reservas:detalle', pk=pk)


# ============================================================
# SERVICIOS ADICIONALES (DETALLE DE LA RESERVA)
# ============================================================
class DetalleReservaCreateView(AdministradorRequeridoMixin, View):
    """Agrega un servicio adicional a la reserva."""

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        formulario = DetalleReservaForm(request.POST, reserva=reserva)
        if formulario.is_valid():
            detalle = formulario.save(commit=False)
            detalle.reserva = reserva
            detalle.save()
            messages.success(request, 'Servicio agregado a la reserva.')
        else:
            for errores in formulario.errors.values():
                for error in errores:
                    messages.error(request, error)
        return redirect('reservas:detalle', pk=pk)


class DetalleReservaDeleteView(AdministradorRequeridoMixin, View):
    """Quita un servicio adicional de la reserva."""

    def post(self, request, pk):
        detalle = get_object_or_404(DetalleReserva, pk=pk)
        id_reserva = detalle.reserva_id
        detalle.delete()
        messages.success(request, 'Servicio eliminado de la reserva.')
        return redirect('reservas:detalle', pk=id_reserva)
