"""
Vistas del modulo CAFETERIA.

CRUD completo de categorias y productos del menu. La consulta esta
disponible para cualquier usuario autenticado; la escritura solo para
el rol Administrador.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from bookspace_manager.vistas import EliminacionProtegidaMixin
from cafeteria.forms import CategoriaMenuForm, ProductoMenuForm
from cafeteria.models import CategoriaMenu, ProductoMenu
from cuentas.mixins import AdministradorRequeridoMixin


# ============================================================
# CATEGORIAS
# ============================================================
class CategoriaListView(LoginRequiredMixin, ListView):
    model = CategoriaMenu
    template_name = 'cafeteria/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 10


class CategoriaCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = CategoriaMenu
    form_class = CategoriaMenuForm
    template_name = 'cafeteria/categoria_form.html'
    success_url = reverse_lazy('cafeteria:categoria_lista')
    success_message = 'Categoria creada correctamente.'


class CategoriaUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = CategoriaMenu
    form_class = CategoriaMenuForm
    template_name = 'cafeteria/categoria_form.html'
    success_url = reverse_lazy('cafeteria:categoria_lista')
    success_message = 'Categoria actualizada correctamente.'


class CategoriaDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = CategoriaMenu
    template_name = 'cafeteria/categoria_confirm_delete.html'
    success_url = reverse_lazy('cafeteria:categoria_lista')
    context_object_name = 'categoria'
    mensaje_protegido = (
        'No se puede eliminar la categoria: tiene productos asociados. '
        'Desactivala en su lugar.'
    )


# ============================================================
# PRODUCTOS
# ============================================================
class ProductoListView(LoginRequiredMixin, ListView):
    model = ProductoMenu
    template_name = 'cafeteria/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 15

    def get_queryset(self):
        registros = ProductoMenu.objects.select_related('categoria')
        consulta = self.request.GET.get('q', '').strip()
        categoria = self.request.GET.get('categoria', '').strip()
        if consulta:
            registros = registros.filter(
                Q(nombre__icontains=consulta) | Q(descripcion__icontains=consulta)
            )
        if categoria.isdigit():
            registros = registros.filter(categoria_id=categoria)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['categorias'] = CategoriaMenu.objects.all()
        return contexto


class ProductoCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    model = ProductoMenu
    form_class = ProductoMenuForm
    template_name = 'cafeteria/producto_form.html'
    success_url = reverse_lazy('cafeteria:producto_lista')
    success_message = 'Producto creado correctamente.'


class ProductoUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = ProductoMenu
    form_class = ProductoMenuForm
    template_name = 'cafeteria/producto_form.html'
    success_url = reverse_lazy('cafeteria:producto_lista')
    success_message = 'Producto actualizado correctamente.'


class ProductoDeleteView(
    AdministradorRequeridoMixin, EliminacionProtegidaMixin, DeleteView
):
    model = ProductoMenu
    template_name = 'cafeteria/producto_confirm_delete.html'
    success_url = reverse_lazy('cafeteria:producto_lista')
    context_object_name = 'producto'
