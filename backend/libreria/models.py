"""
Modulo LIBRERIA
---------------
Libros de Raccoon Cafe, en dos categorias:

    - venta   : se venden; exigen un precio mayor a 0.
    - lectura : se consultan en la cafeteria; no se venden, su precio es 0
                y exigen estante.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Libro(models.Model):
    class Tipo(models.TextChoices):
        VENTA = 'venta', 'Para vender'
        LECTURA = 'lectura', 'Para leer en la cafetería'

    class Condicion(models.TextChoices):
        NUEVO = 'nuevo', 'Nuevo'
        EXCELENTE = 'excelente', 'Excelente'
        BUENO = 'bueno', 'Buen estado'
        ACEPTABLE = 'aceptable', 'Aceptable'

    id = models.BigAutoField(primary_key=True, db_column='id_libro')
    titulo = models.CharField(max_length=160, db_column='titulo')
    autor = models.CharField(max_length=120, db_column='autor')
    genero = models.CharField(max_length=60, blank=True, db_column='genero')

    tipo = models.CharField(
        max_length=10, choices=Tipo.choices, default=Tipo.VENTA, db_column='tipo'
    )
    condicion = models.CharField(
        max_length=10, choices=Condicion.choices, blank=True, db_column='condicion'
    )

    precio = models.DecimalField(
        max_digits=7, decimal_places=2, default=0, db_column='precio'
    )
    stock = models.PositiveIntegerField(default=1, db_column='stock')
    estante = models.CharField(
        max_length=10,
        blank=True,
        db_column='estante',
        help_text='Ubicación física, por ejemplo A1 o B2.',
    )

    disponible = models.BooleanField(default=True, db_column='disponible')
    creado_en = models.DateTimeField(auto_now_add=True, db_column='creado_en')
    actualizado_en = models.DateTimeField(auto_now=True, db_column='actualizado_en')

    class Meta:
        db_table = 'libreria_libro'
        ordering = ['titulo']
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0),
                name='libreria_precio_no_negativo',
            ),
        ]

    def clean(self):
        if self.tipo == self.Tipo.LECTURA:
            # La biblioteca del cafe no se vende, no tiene condicion y
            # necesita ubicacion fisica.
            self.precio = Decimal('0.00')
            self.condicion = ''
            if not self.estante:
                raise ValidationError({
                    'estante': 'Un libro para leer en la cafetería debe indicar su estante.'
                })
        elif self.tipo == self.Tipo.VENTA:
            if self.precio is None or self.precio <= 0:
                raise ValidationError({
                    'precio': 'Un libro para vender debe tener un precio mayor a 0.'
                })

    @property
    def en_venta(self):
        return self.tipo == self.Tipo.VENTA

    def __str__(self):
        return f'{self.titulo} — {self.autor}'
