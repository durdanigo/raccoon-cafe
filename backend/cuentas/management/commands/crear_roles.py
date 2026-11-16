"""
Comando: python manage.py crear_roles

Crea los grupos 'Administrador' y 'Cliente' y les asigna los permisos
correspondientes. Se ejecuta una sola vez despues de las migraciones.
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from cuentas.mixins import GRUPO_ADMINISTRADOR, GRUPO_CLIENTE


class Command(BaseCommand):
    help = 'Crea los grupos de roles del sistema (Administrador y Cliente).'

    def handle(self, *args, **options):
        grupo_admin, creado_admin = Group.objects.get_or_create(
            name=GRUPO_ADMINISTRADOR
        )
        grupo_cliente, creado_cliente = Group.objects.get_or_create(
            name=GRUPO_CLIENTE
        )

        # El administrador recibe todos los permisos de los modulos del sistema.
        permisos = Permission.objects.filter(
            content_type__app_label__in=[
                'espacios',
                'clientes',
                'reservas',
                'pagos',
            ]
        )
        grupo_admin.permissions.set(permisos)

        # El cliente solo puede crear y consultar sus propias reservas.
        permisos_cliente = Permission.objects.filter(
            content_type__app_label='reservas',
            codename__in=['add_reserva', 'view_reserva', 'change_reserva'],
        )
        grupo_cliente.permissions.set(permisos_cliente)

        self.stdout.write(
            self.style.SUCCESS(
                f'Grupo "{GRUPO_ADMINISTRADOR}": '
                f'{"creado" if creado_admin else "ya existia"} '
                f'({grupo_admin.permissions.count()} permisos)'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Grupo "{GRUPO_CLIENTE}": '
                f'{"creado" if creado_cliente else "ya existia"} '
                f'({grupo_cliente.permissions.count()} permisos)'
            )
        )
