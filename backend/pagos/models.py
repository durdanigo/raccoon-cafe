"""
Modulo PAGOS
------------
Registra los abonos que realizan los clientes sobre una reserva.

Reglas de negocio implementadas:
    1. El monto debe ser mayor a cero.
    2. Un pago no puede exceder el saldo pendiente de la reserva.
    3. Al confirmarse un pago que cubre el total, la reserva pasa
       automaticamente al estado CONFIRMADA.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from reservas.models import Reserva


class Pago(models.Model):
    """Abono economico asociado a una reserva."""

    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TARJETA = 'TARJETA', 'Tarjeta de credito/debito'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia bancaria'

    class Estado(models.TextChoices):
        REGISTRADO = 'REGISTRADO', 'Registrado'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        ANULADO = 'ANULADO', 'Anulado'

    id_pago = models.BigAutoField(primary_key=True, db_column='id_pago')
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.PROTECT,
        related_name='pagos_de_reserva',
        db_column='id_reserva',
        verbose_name='Reserva',
    )
    fecha_pago = models.DateTimeField(
        auto_now_add=True, db_column='fecha_pago', verbose_name='Fecha del pago'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        db_column='monto',
        verbose_name='Monto (USD)',
    )
    metodo_pago = models.CharField(
        max_length=15,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
        db_column='metodo_pago',
        verbose_name='Metodo de pago',
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.CONFIRMADO,
        db_column='estado',
        verbose_name='Estado',
    )
    referencia = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        db_column='referencia',
        verbose_name='Referencia / comprobante',
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='pagos_registrados',
        db_column='id_usuario_registro',
        verbose_name='Registrado por',
    )

    class Meta:
        db_table = 'pago'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name='pago_monto_positivo',
            ),
        ]

    def __str__(self):
        return f'{self.reserva.codigo} - ${self.monto} ({self.get_metodo_pago_display()})'

    def clean(self):
        errores = {}

        if self.monto is not None and self.monto <= Decimal('0.00'):
            errores['monto'] = 'El monto debe ser mayor a cero.'

        if self.reserva_id and self.monto:
            if self.reserva.estado == Reserva.Estado.CANCELADA:
                errores['reserva'] = 'No se pueden registrar pagos de una reserva cancelada.'
            else:
                saldo = self.reserva.saldo_pendiente
                if self.pk:
                    anterior = Pago.objects.filter(pk=self.pk).first()
                    if anterior and anterior.estado == Pago.Estado.CONFIRMADO:
                        saldo += anterior.monto
                if self.estado == Pago.Estado.CONFIRMADO and self.monto > saldo:
                    errores['monto'] = (
                        f'El monto supera el saldo pendiente de la reserva '
                        f'(${saldo}).'
                    )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actualizar_estado_reserva()

    def delete(self, *args, **kwargs):
        reserva = self.reserva
        super().delete(*args, **kwargs)
        Pago._sincronizar_reserva(reserva)

    def actualizar_estado_reserva(self):
        Pago._sincronizar_reserva(self.reserva)

    @staticmethod
    def _sincronizar_reserva(reserva):
        """Confirma la reserva cuando queda totalmente pagada."""
        reserva.refresh_from_db()
        if reserva.estado == Reserva.Estado.CANCELADA:
            return
        if reserva.esta_pagada and reserva.estado == Reserva.Estado.PENDIENTE:
            Reserva.objects.filter(pk=reserva.pk).update(
                estado=Reserva.Estado.CONFIRMADA
            )
        elif not reserva.esta_pagada and reserva.estado == Reserva.Estado.CONFIRMADA:
            Reserva.objects.filter(pk=reserva.pk).update(
                estado=Reserva.Estado.PENDIENTE
            )
