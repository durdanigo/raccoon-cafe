"""
Modulo RESERVAS
---------------
Nucleo del sistema. Una Reserva ocupa un Espacio en una fecha y
franja horaria determinada, y puede incluir Servicios adicionales
a traves de DetalleReserva.

Reglas de negocio implementadas:
    1. La hora de fin debe ser mayor a la hora de inicio.
    2. La reserva debe estar dentro del horario de atencion.
    3. El numero de personas no puede superar la capacidad del espacio.
    4. Un espacio no puede tener dos reservas vigentes que se crucen.
    5. El total se calcula automaticamente al guardar:
       total = (tarifa_hora * horas) + servicios adicionales.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from clientes.models import Cliente
from espacios.models import Espacio, Servicio

CENTAVOS = Decimal('0.01')


class Reserva(models.Model):
    """Ocupacion de un espacio por parte de un cliente."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        COMPLETADA = 'COMPLETADA', 'Completada'

    ESTADOS_VIGENTES = [Estado.PENDIENTE, Estado.CONFIRMADA]

    id_reserva = models.BigAutoField(primary_key=True, db_column='id_reserva')
    codigo = models.CharField(
        max_length=15,
        unique=True,
        editable=False,
        db_column='codigo',
        verbose_name='Codigo',
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='reservas_del_cliente',
        db_column='id_cliente',
        verbose_name='Cliente',
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.PROTECT,
        related_name='reservas_del_espacio',
        db_column='id_espacio',
        verbose_name='Espacio',
    )
    fecha = models.DateField(db_column='fecha', verbose_name='Fecha de la reserva')
    hora_inicio = models.TimeField(db_column='hora_inicio', verbose_name='Hora de inicio')
    hora_fin = models.TimeField(db_column='hora_fin', verbose_name='Hora de fin')
    numero_personas = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        db_column='numero_personas',
        verbose_name='Numero de personas',
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_column='estado',
        verbose_name='Estado',
    )
    observaciones = models.TextField(
        null=True, blank=True, db_column='observaciones', verbose_name='Observaciones'
    )
    subtotal_espacio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        db_column='subtotal_espacio',
        verbose_name='Subtotal del espacio',
    )
    subtotal_servicios = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        db_column='subtotal_servicios',
        verbose_name='Subtotal de servicios',
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        db_column='total',
        verbose_name='Total a pagar',
    )
    registrada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reservas_registradas',
        db_column='id_usuario_registro',
        verbose_name='Registrada por',
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, db_column='fecha_registro', verbose_name='Fecha de registro'
    )

    class Meta:
        db_table = 'reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', '-hora_inicio']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F('hora_inicio')),
                name='reserva_hora_fin_mayor_inicio',
            ),
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name='reserva_total_no_negativo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.espacio.codigo} ({self.fecha})'

    # ------------------------------------------------------------------
    # Calculos
    # ------------------------------------------------------------------
    @property
    def horas(self):
        """Duracion de la reserva expresada en horas decimales."""
        if not self.hora_inicio or not self.hora_fin:
            return Decimal('0.00')
        minutos_inicio = self.hora_inicio.hour * 60 + self.hora_inicio.minute
        minutos_fin = self.hora_fin.hour * 60 + self.hora_fin.minute
        diferencia = max(minutos_fin - minutos_inicio, 0)
        return (Decimal(diferencia) / Decimal(60)).quantize(CENTAVOS)

    def calcular_subtotal_servicios(self):
        """Suma los servicios adicionales ya guardados de la reserva."""
        if not self.pk:
            return Decimal('0.00')
        agregado = self.detalles_de_reserva.aggregate(suma=Sum('subtotal'))
        return (agregado['suma'] or Decimal('0.00')).quantize(CENTAVOS)

    def recalcular_totales(self, guardar=True):
        """Recalcula subtotales y total de la reserva."""
        tarifa = self.espacio.tarifa_hora if self.espacio_id else Decimal('0.00')
        self.subtotal_espacio = (tarifa * self.horas).quantize(CENTAVOS)
        self.subtotal_servicios = self.calcular_subtotal_servicios()
        self.total = (self.subtotal_espacio + self.subtotal_servicios).quantize(CENTAVOS)
        if guardar and self.pk:
            super().save(
                update_fields=['subtotal_espacio', 'subtotal_servicios', 'total']
            )
        return self.total

    @property
    def total_pagado(self):
        """Suma de los pagos confirmados de la reserva."""
        if not self.pk:
            return Decimal('0.00')
        agregado = self.pagos_de_reserva.filter(estado='CONFIRMADO').aggregate(
            suma=Sum('monto')
        )
        return (agregado['suma'] or Decimal('0.00')).quantize(CENTAVOS)

    @property
    def saldo_pendiente(self):
        return (self.total - self.total_pagado).quantize(CENTAVOS)

    @property
    def esta_pagada(self):
        return self.total > 0 and self.saldo_pendiente <= Decimal('0.00')

    # ------------------------------------------------------------------
    # Validaciones de negocio
    # ------------------------------------------------------------------
    def clean(self):
        errores = {}

        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            errores['hora_fin'] = 'La hora de fin debe ser posterior a la hora de inicio.'

        apertura = getattr(settings, 'HORA_APERTURA', 7)
        cierre = getattr(settings, 'HORA_CIERRE', 22)
        if self.hora_inicio and self.hora_inicio.hour < apertura:
            errores['hora_inicio'] = f'El coworking abre a las {apertura:02d}:00.'
        if self.hora_fin and (
            self.hora_fin.hour > cierre
            or (self.hora_fin.hour == cierre and self.hora_fin.minute > 0)
        ):
            errores['hora_fin'] = f'El coworking cierra a las {cierre:02d}:00.'

        if self.espacio_id:
            if self.numero_personas and self.numero_personas > self.espacio.capacidad:
                errores['numero_personas'] = (
                    f'El espacio {self.espacio.codigo} admite como maximo '
                    f'{self.espacio.capacidad} persona(s).'
                )
            if (
                self.espacio.estado != Espacio.Estado.DISPONIBLE
                and self.estado in self.ESTADOS_VIGENTES
            ):
                errores['espacio'] = (
                    'El espacio seleccionado no esta disponible para reservas.'
                )

        # Regla 4: no se permiten cruces de horario en el mismo espacio.
        if self.espacio_id and self.fecha and self.hora_inicio and self.hora_fin:
            if self.estado in self.ESTADOS_VIGENTES:
                cruces = Reserva.objects.filter(
                    espacio=self.espacio,
                    fecha=self.fecha,
                    estado__in=self.ESTADOS_VIGENTES,
                    hora_inicio__lt=self.hora_fin,
                    hora_fin__gt=self.hora_inicio,
                ).exclude(pk=self.pk)
                if cruces.exists():
                    ocupada = cruces.first()
                    errores['hora_inicio'] = (
                        f'El espacio ya esta reservado de '
                        f'{ocupada.hora_inicio.strftime("%H:%M")} a '
                        f'{ocupada.hora_fin.strftime("%H:%M")} '
                        f'(reserva {ocupada.codigo}).'
                    )

        if errores:
            raise ValidationError(errores)

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def _generar_codigo(self):
        ultimo = Reserva.objects.order_by('-id_reserva').first()
        siguiente = (ultimo.id_reserva + 1) if ultimo else 1
        return f'RSV-{siguiente:06d}'

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generar_codigo()
        tarifa = self.espacio.tarifa_hora if self.espacio_id else Decimal('0.00')
        self.subtotal_espacio = (tarifa * self.horas).quantize(CENTAVOS)
        self.subtotal_servicios = self.calcular_subtotal_servicios()
        self.total = (self.subtotal_espacio + self.subtotal_servicios).quantize(CENTAVOS)
        super().save(*args, **kwargs)


class DetalleReserva(models.Model):
    """Servicio adicional contratado dentro de una reserva."""

    id_detalle_reserva = models.BigAutoField(
        primary_key=True, db_column='id_detalle_reserva'
    )
    # CASCADE unicamente en la relacion maestro-detalle: si se elimina la
    # reserva, sus lineas de detalle carecen de sentido por si solas.
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='detalles_de_reserva',
        db_column='id_reserva',
        verbose_name='Reserva',
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        related_name='detalles_del_servicio',
        db_column='id_servicio',
        verbose_name='Servicio',
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        db_column='cantidad',
        verbose_name='Cantidad',
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        db_column='precio_unitario',
        verbose_name='Precio unitario',
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        db_column='subtotal',
        verbose_name='Subtotal',
    )

    class Meta:
        db_table = 'detalle_reserva'
        verbose_name = 'Detalle de reserva'
        verbose_name_plural = 'Detalles de reserva'
        ordering = ['id_detalle_reserva']
        constraints = [
            models.UniqueConstraint(
                fields=['reserva', 'servicio'],
                name='detalle_servicio_unico_por_reserva',
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=1),
                name='detalle_cantidad_positiva',
            ),
        ]

    def __str__(self):
        return f'{self.reserva.codigo} - {self.servicio.nombre} x{self.cantidad}'

    def save(self, *args, **kwargs):
        # El precio se congela al momento de contratar el servicio.
        self.precio_unitario = self.servicio.precio
        self.subtotal = (self.precio_unitario * self.cantidad).quantize(CENTAVOS)
        super().save(*args, **kwargs)
        self.reserva.recalcular_totales()

    def delete(self, *args, **kwargs):
        reserva = self.reserva
        super().delete(*args, **kwargs)
        reserva.recalcular_totales()
