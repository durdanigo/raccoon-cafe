"""
Vistas del modulo LIBRERIA.

CRUD completo de libros. La consulta esta disponible para cualquier
usuario autenticado; la escritura solo para el rol Administrador.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from bookspace_manager.vistas import EliminacionProtegidaMixin
from cuentas.mixins import AdministradorRequeridoMixin
from libreria.forms import LibroForm
from libreria.models import Libro


class LibroListView(LoginRequiredMixin, ListView):
    model = Libro
    template_name = 'libreria/libro_list.html'
    context_object_name = 'libros'
    paginate_by = 15

    def get_queryset(self):
        registros = Libro.objects.all()
        consulta = self.request.GET.get('q', '').strip()
        tipo = self.request.GET.get('tipo', '').strip()
        if consulta:
            registros = registros.filter(
                Q(titulo__icontains=consulta)
                | Q(autor__icontains=consulta)
                | Q(genero__icontains=consulta)
            )
        if tipo in Libro.Tipo.values:
            registros = registros.filter(tipo=tipo)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['tipos'] = Libro.Tipo.choices
        return contexto


class LibroCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = Libro
    form_class = LibroForm
    template_name = 'libreria/libro_form.html'
    success_url = reverse_lazy('libreria:libro_lista')
    success_message = 'Libro registrado correctamente.'


class LibroUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = Libro
    form_class = LibroForm
    template_name = 'libreria/libro_form.html'
    success_url = reverse_lazy('libreria:libro_lista')
    success_message = 'Libro actualizado correctamente.'


class LibroDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = Libro
    template_name = 'libreria/libro_confirm_delete.html'
    success_url = reverse_lazy('libreria:libro_lista')
    context_object_name = 'libro'
