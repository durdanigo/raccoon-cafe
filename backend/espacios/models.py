"""
Modulo ESPACIOS
---------------
Administra el catalogo fisico del coworking:
    - TipoEspacio : clasificacion de los espacios (sala, escritorio, oficina).
    - Espacio     : cada unidad reservable, con su capacidad y tarifa por hora.
    - Servicio    : servicios adicionales que se pueden agregar a una reserva.
"""

from django.core.validators import MinValueValidator
from django.db import models


class TipoEspacio(models.Model):
    """Clasificacion de los espacios del coworking."""

    id_tipo_espacio = models.BigAutoField(primary_key=True, db_column='id_tipo_espacio')
    nombre = models.CharField(
        max_length=60, unique=True, db_column='nombre', verbose_name='Nombre'
    )
    descripcion = models.TextField(
        null=True, blank=True, db_column='descripcion', verbose_name='Descripcion'
    )
    activo = models.BooleanField(default=True, db_column='activo', verbose_name='Activo')

    class Meta:
        db_table = 'tipo_espacio'
        verbose_name = 'Tipo de espacio'
        verbose_name_plural = 'Tipos de espacio'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Espacio(models.Model):
    """Unidad fisica reservable dentro del coworking."""

    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En mantenimiento'
        INACTIVO = 'INACTIVO', 'Inactivo'

    id_espacio = models.BigAutoField(primary_key=True, db_column='id_espacio')
    tipo_espacio = models.ForeignKey(
        TipoEspacio,
        on_delete=models.PROTECT,
        related_name='espacios_del_tipo',
        db_column='id_tipo_espacio',
        verbose_name='Tipo de espacio',
    )
    codigo = models.CharField(
        max_length=15, unique=True, db_column='codigo', verbose_name='Codigo'
    )
    nombre = models.CharField(max_length=100, db_column='nombre', verbose_name='Nombre')
    ubicacion = models.CharField(
        max_length=120, db_column='ubicacion', verbose_name='Ubicacion'
    )
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        db_column='capacidad',
        verbose_name='Capacidad (personas)',
    )
    tarifa_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='tarifa_hora',
        verbose_name='Tarifa por hora (USD)',
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        db_column='estado',
        verbose_name='Estado',
    )
    descripcion = models.TextField(
        null=True, blank=True, db_column='descripcion', verbose_name='Descripcion'
    )

    class Meta:
        db_table = 'espacio'
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['codigo']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacidad__gte=1),
                name='espacio_capacidad_positiva',
            ),
            models.CheckConstraint(
                condition=models.Q(tarifa_hora__gte=0),
                name='espacio_tarifa_no_negativa',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    @property
    def esta_disponible(self):
        return self.estado == self.Estado.DISPONIBLE


class Servicio(models.Model):
    """Servicio adicional que puede agregarse a una reserva."""

    id_servicio = models.BigAutoField(primary_key=True, db_column='id_servicio')
    nombre = models.CharField(
        max_length=80, unique=True, db_column='nombre', verbose_name='Nombre'
    )
    descripcion = models.TextField(
        null=True, blank=True, db_column='descripcion', verbose_name='Descripcion'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='precio',
        verbose_name='Precio unitario (USD)',
    )
    activo = models.BooleanField(default=True, db_column='activo', verbose_name='Activo')

    class Meta:
        db_table = 'servicio'
        verbose_name = 'Servicio adicional'
        verbose_name_plural = 'Servicios adicionales'
        ordering = ['nombre']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0),
                name='servicio_precio_no_negativo',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} (${self.precio})'
