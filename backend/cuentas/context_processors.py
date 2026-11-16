"""Datos de sesion disponibles en todas las plantillas."""

from cuentas.mixins import cliente_de, es_administrador


def datos_de_sesion(request):
    usuario = request.user
    return {
        'es_administrador': es_administrador(usuario),
        'cliente_actual': cliente_de(usuario) if usuario.is_authenticated else None,
    }
