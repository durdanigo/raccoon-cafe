"""
Modulo CLIENTES
---------------
Registra a las personas y empresas que reservan espacios.
Cada cliente puede tener (opcionalmente) una cuenta de usuario
asociada, lo que le permite iniciar sesion y ver sus reservas.
"""

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

validador_cedula = RegexValidator(
    regex=r'^\d{10}$',
    message='La cedula debe tener exactamente 10 digitos numericos.',
)


class Cliente(models.Model):
    """Persona natural o representante de empresa que realiza reservas."""

    class TipoCliente(models.TextChoices):
        PERSONAL = 'PERSONAL', 'Personal'
        EMPRESARIAL = 'EMPRESARIAL', 'Empresarial'

    id_cliente = models.BigAutoField(primary_key=True, db_column='id_cliente')
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cliente_asociado',
        db_column='id_usuario',
        verbose_name='Cuenta de usuario',
    )
    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[validador_cedula],
        db_column='cedula',
        verbose_name='Cedula',
    )
    nombres = models.CharField(max_length=80, db_column='nombres', verbose_name='Nombres')
    apellidos = models.CharField(
        max_length=80, db_column='apellidos', verbose_name='Apellidos'
    )
    correo = models.EmailField(
        max_length=120, unique=True, db_column='correo', verbose_name='Correo electronico'
    )
    telefono = models.CharField(
        max_length=15, db_column='telefono', verbose_name='Telefono'
    )
    empresa = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        db_column='empresa',
        verbose_name='Empresa',
    )
    tipo_cliente = models.CharField(
        max_length=12,
        choices=TipoCliente.choices,
        default=TipoCliente.PERSONAL,
        db_column='tipo_cliente',
        verbose_name='Tipo de cliente',
    )
    activo = models.BooleanField(default=True, db_column='activo', verbose_name='Activo')
    fecha_registro = models.DateTimeField(
        auto_now_add=True, db_column='fecha_registro', verbose_name='Fecha de registro'
    )

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.apellidos} {self.nombres} - {self.cedula}'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'
