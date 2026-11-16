"""
Vistas del modulo ESPACIOS.

Se implementan tres CRUD completos con vistas basadas en clases:
    - TipoEspacio
    - Espacio
    - Servicio

La consulta (list/detail) esta disponible para cualquier usuario
autenticado; la escritura (create/update/delete) solo para el rol
Administrador.
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

from bookspace_manager.vistas import EliminacionProtegidaMixin
from cuentas.mixins import AdministradorRequeridoMixin
from espacios.forms import EspacioForm, ServicioForm, TipoEspacioForm
from espacios.models import Espacio, Servicio, TipoEspacio


# ============================================================
# CRUD DE TIPO DE ESPACIO
# ============================================================
class TipoEspacioListView(LoginRequiredMixin, ListView):
    model = TipoEspacio
    template_name = 'espacios/tipoespacio_list.html'
    context_object_name = 'tipos'
    paginate_by = 10

    def get_queryset(self):
        consulta = self.request.GET.get('q', '').strip()
        registros = TipoEspacio.objects.all()
        if consulta:
            registros = registros.filter(nombre__icontains=consulta)
        return registros


class TipoEspacioDetailView(LoginRequiredMixin, DetailView):
    model = TipoEspacio
    template_name = 'espacios/tipoespacio_detail.html'
    context_object_name = 'tipo'


class TipoEspacioCreateView(
    AdministradorRequeridoMixin, SuccessMessageMixin, CreateView
):
    model = TipoEspacio
    form_class = TipoEspacioForm
    template_name = 'espacios/tipoespacio_form.html'
    success_url = reverse_lazy('espacios:tipo_lista')
    success_message = 'Tipo de espacio creado correctamente.'


class TipoEspacioUpdateView(
    AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView
):
    model = TipoEspacio
    form_class = TipoEspacioForm
    template_name = 'espacios/tipoespacio_form.html'
    success_url = reverse_lazy('espacios:tipo_lista')
    success_message = 'Tipo de espacio actualizado correctamente.'


class TipoEspacioDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = TipoEspacio
    template_name = 'espacios/tipoespacio_confirm_delete.html'
    success_url = reverse_lazy('espacios:tipo_lista')
    context_object_name = 'tipo'
    mensaje_protegido = (
        'No se puede eliminar el tipo: existen espacios registrados con el.'
    )


# ============================================================
# CRUD DE ESPACIO
# ============================================================
class EspacioListView(LoginRequiredMixin, ListView):
    model = Espacio
    template_name = 'espacios/espacio_list.html'
    context_object_name = 'espacios'
    paginate_by = 10

    def get_queryset(self):
        registros = Espacio.objects.select_related('tipo_espacio')
        consulta = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip()
        if consulta:
            registros = registros.filter(
                Q(codigo__icontains=consulta)
                | Q(nombre__icontains=consulta)
                | Q(ubicacion__icontains=consulta)
            )
        if estado:
            registros = registros.filter(estado=estado)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['estados'] = Espacio.Estado.choices
        return contexto


class EspacioDetailView(LoginRequiredMixin, DetailView):
    model = Espacio
    template_name = 'espacios/espacio_detail.html'
    context_object_name = 'espacio'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['reservas_recientes'] = self.object.reservas_del_espacio.select_related(
            'cliente'
        )[:5]
        return contexto


class EspacioCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = Espacio
    form_class = EspacioForm
    template_name = 'espacios/espacio_form.html'
    success_url = reverse_lazy('espacios:espacio_lista')
    success_message = 'Espacio creado correctamente.'


class EspacioUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = Espacio
    form_class = EspacioForm
    template_name = 'espacios/espacio_form.html'
    success_url = reverse_lazy('espacios:espacio_lista')
    success_message = 'Espacio actualizado correctamente.'


class EspacioDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = Espacio
    template_name = 'espacios/espacio_confirm_delete.html'
    success_url = reverse_lazy('espacios:espacio_lista')
    context_object_name = 'espacio'
    mensaje_protegido = (
        'No se puede eliminar el espacio: tiene reservas asociadas. '
        'Cambialo a estado Inactivo.'
    )


# ============================================================
# CRUD DE SERVICIO ADICIONAL
# ============================================================
class ServicioListView(LoginRequiredMixin, ListView):
    model = Servicio
    template_name = 'espacios/servicio_list.html'
    context_object_name = 'servicios'
    paginate_by = 10

    def get_queryset(self):
        consulta = self.request.GET.get('q', '').strip()
        registros = Servicio.objects.all()
        if consulta:
            registros = registros.filter(nombre__icontains=consulta)
        return registros


class ServicioDetailView(LoginRequiredMixin, DetailView):
    model = Servicio
    template_name = 'espacios/servicio_detail.html'
    context_object_name = 'servicio'


class ServicioCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'espacios/servicio_form.html'
    success_url = reverse_lazy('espacios:servicio_lista')
    success_message = 'Servicio creado correctamente.'


class ServicioUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'espacios/servicio_form.html'
    success_url = reverse_lazy('espacios:servicio_lista')
    success_message = 'Servicio actualizado correctamente.'


class ServicioDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = Servicio
    template_name = 'espacios/servicio_confirm_delete.html'
    success_url = reverse_lazy('espacios:servicio_lista')
    context_object_name = 'servicio'
    mensaje_protegido = (
        'No se puede eliminar el servicio: esta incluido en reservas existentes.'
    )
