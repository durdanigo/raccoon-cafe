"""
Vistas del modulo CUENTAS.

Implementa el inicio y cierre de sesion, el registro publico de
clientes y la pantalla de perfil.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from cuentas.forms import LoginForm, RegistroClienteForm
from cuentas.mixins import GRUPO_CLIENTE, cliente_de


class IniciarSesionView(LoginView):
    template_name = 'cuentas/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request, f'Bienvenida/o de nuevo, {form.get_user().username}.'
        )
        return super().form_valid(form)


class CerrarSesionView(LogoutView):
    next_page = reverse_lazy('cuentas:login')


class RegistroClienteView(CreateView):
    """Registro publico: crea el usuario, su perfil y lo agrega al grupo Cliente."""

    form_class = RegistroClienteForm
    template_name = 'cuentas/registro.html'
    success_url = reverse_lazy('panel:dashboard')

    def dispatch(self, request, *args, **kwargs):
        # Quien ya inicio sesion no necesita registrarse de nuevo.
        if request.user.is_authenticated:
            return redirect('panel:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        grupo, _ = Group.objects.get_or_create(name=GRUPO_CLIENTE)
        self.object.groups.add(grupo)
        login(self.request, self.object)
        messages.success(
            self.request,
            'Tu cuenta fue creada. Ya puedes reservar un espacio.',
        )
        return respuesta


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'cuentas/perfil.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        cliente = cliente_de(self.request.user)
        contexto['cliente'] = cliente
        if cliente:
            contexto['reservas'] = cliente.reservas_del_cliente.select_related(
                'espacio'
            )[:5]
        return contexto
