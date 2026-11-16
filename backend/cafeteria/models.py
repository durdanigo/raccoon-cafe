"""
Modulo CAFETERIA
----------------
Carta de Raccoon Cafe:
    - CategoriaMenu : agrupa la carta (Calientes, Frias, Pasteleria, Packs).
    - ProductoMenu  : cada item de la carta, con inventario opcional.
"""

from django.core.exceptions import ValidationError
from django.db import models


class CategoriaMenu(models.Model):
    """Agrupa la carta: Calientes, Frias e Infusiones, Pasteleria, Packs."""

    id = models.BigAutoField(primary_key=True, db_column='id_categoria_menu')
    nombre = models.CharField(max_length=60, unique=True, db_column='nombre')
    descripcion = models.CharField(max_length=200, blank=True, db_column='descripcion')
    orden = models.PositiveSmallIntegerField(
        default=0, db_column='orden', help_text='Orden de aparicion en la carta.'
    )
    activa = models.BooleanField(default=True, db_column='activa')

    class Meta:
        db_table = 'cafeteria_categoria'
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoría del menú'
        verbose_name_plural = 'Categorías del menú'

    def __str__(self):
        return self.nombre


class ProductoMenu(models.Model):
    """Un item de la carta de cafeteria."""

    id = models.BigAutoField(primary_key=True, db_column='id_producto_menu')
    categoria = models.ForeignKey(
        CategoriaMenu,
        on_delete=models.PROTECT,
        related_name='productos',
        db_column='id_categoria_menu',
    )
    nombre = models.CharField(max_length=120, db_column='nombre')
    descripcion = models.TextField(blank=True, db_column='descripcion')
    precio = models.DecimalField(max_digits=7, decimal_places=2, db_column='precio')

    # Una bebida se prepara al momento y no lleva inventario; la pasteleria si.
    controla_stock = models.BooleanField(default=False, db_column='controla_stock')
    stock = models.PositiveIntegerField(default=0, db_column='stock')
    stock_minimo = models.PositiveIntegerField(default=3, db_column='stock_minimo')

    disponible = models.BooleanField(default=True, db_column='disponible')
    creado_en = models.DateTimeField(auto_now_add=True, db_column='creado_en')
    actualizado_en = models.DateTimeField(auto_now=True, db_column='actualizado_en')

    class Meta:
        db_table = 'cafeteria_producto'
        ordering = ['categoria__orden', 'nombre']
        verbose_name = 'Producto de cafetería'
        verbose_name_plural = 'Productos de cafetería'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gte=0),
                name='cafeteria_precio_no_negativo',
            ),
        ]

    def clean(self):
        if self.precio is not None and self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo.'})
        if not self.controla_stock:
            # Sin control de inventario, el stock no significa nada: se normaliza.
            self.stock = 0

    @property
    def bajo_stock(self):
        """True cuando el inventario llego al umbral de reposicion."""
        return self.controla_stock and self.stock <= self.stock_minimo

    def __str__(self):
        return f'{self.nombre} (${self.precio})'
