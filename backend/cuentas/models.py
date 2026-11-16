"""
Modulo CUENTAS
--------------
Este modulo no define modelos propios: reutiliza el modelo User de
django.contrib.auth y los grupos 'Administrador' y 'Cliente' para el
control de roles. El perfil del cliente vive en clientes.Cliente,
enlazado al usuario mediante un OneToOneField.
"""
