"""
Permisos de la API.

La lectura del catalogo es publica (el sitio web y la app movil la
consumen sin iniciar sesion). Escribir, en cambio, queda reservado a los
usuarios con rol Administrador, identificados con su token.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from cuentas.mixins import es_administrador


class EsAdministrador(BasePermission):
    """Solo administradores autenticados."""

    def has_permission(self, request, view):
        return bool(request.user and es_administrador(request.user))


class EsAdministradorOSoloLectura(BasePermission):
    """Cualquiera puede leer; solo un administrador puede modificar."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and es_administrador(request.user))
