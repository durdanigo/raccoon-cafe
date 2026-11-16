"""
Control de acceso por roles.

Roles del sistema:
    - Administrador : superusuario, staff o miembro del grupo 'Administrador'.
                      Accede a todos los modulos y a toda la informacion.
    - Cliente       : miembro del grupo 'Cliente'. Solo puede ver y gestionar
                      sus propias reservas y pagos.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

GRUPO_ADMINISTRADOR = 'Administrador'
GRUPO_CLIENTE = 'Cliente'


def es_administrador(usuario):
    """Indica si el usuario tiene privilegios de administrador."""
    if not usuario.is_authenticated:
        return False
    return (
        usuario.is_superuser
        or usuario.is_staff
        or usuario.groups.filter(name=GRUPO_ADMINISTRADOR).exists()
    )


def cliente_de(usuario):
    """Devuelve el Cliente asociado al usuario, o None si no tiene."""
    return getattr(usuario, 'cliente_asociado', None)


class AdministradorRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe la vista a usuarios con rol de administrador."""

    def test_func(self):
        return es_administrador(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                'No tienes permisos para acceder a esa seccion.',
            )
            return redirect('panel:dashboard')
        return super().handle_no_permission()
