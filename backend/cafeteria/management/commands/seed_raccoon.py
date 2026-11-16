"""
Comando: python manage.py seed_raccoon

Carga el catalogo inicial de Raccoon Cafe (menu de cafeteria y libros).
Es idempotente: usa get_or_create, no modifica ni borra registros que
ya existan.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from cafeteria.models import CategoriaMenu, ProductoMenu
from libreria.models import Libro

CATEGORIAS = [
    ('Calientes', 1),
    ('Frías e Infusiones', 2),
    ('Pastelería & Snacks', 3),
    ('Packs para Eventos', 4),
]

# (nombre, categoria, precio, controla_stock, stock, stock_minimo)
PRODUCTOS = [
    ('Espresso Raccoon', 'Calientes', '2.00', False, 0, 3),
    ('Americano Doble', 'Calientes', '2.50', False, 0, 3),
    ('Cappuccino Tradicional', 'Calientes', '3.25', False, 0, 3),
    ('Flat White Vainilla', 'Calientes', '3.75', False, 0, 3),
    ('Latte Caramelo / Moca', 'Calientes', '4.00', False, 0, 3),
    ('Iced Matcha Latte', 'Frías e Infusiones', '4.25', False, 0, 3),
    ('Cold Brew Raccoon', 'Frías e Infusiones', '3.50', False, 0, 3),
    ('Infusión Frutos Rojos', 'Frías e Infusiones', '2.75', False, 0, 3),
    ('Croissant de Mantequilla', 'Pastelería & Snacks', '2.50', True, 18, 5),
    ('Croissant de Almendras', 'Pastelería & Snacks', '3.25', True, 12, 5),
    ('Tarta de Zanahoria', 'Pastelería & Snacks', '3.75', True, 10, 3),
    ('Brownie con Sal Marina', 'Pastelería & Snacks', '2.80', True, 14, 4),
    ('Toast de Aguacate', 'Pastelería & Snacks', '4.50', True, 8, 3),
    ('Pack Taller Básico', 'Packs para Eventos', '22.00', False, 0, 3),
    ('Pack Fiesta Social', 'Packs para Eventos', '35.00', False, 0, 3),
]

# (titulo, autor, tipo, condicion, precio, stock, estante)
LIBROS = [
    ('Cien Años de Soledad', 'Gabriel García Márquez', 'venta', 'nuevo', '18.50', 4, ''),
    ('Hábitos Atómicos', 'James Clear', 'venta', 'nuevo', '21.00', 6, ''),
    ('Klara y el Sol', 'Kazuo Ishiguro', 'venta', 'nuevo', '19.00', 3, ''),
    ('Harry Potter y el Prisionero de Azkaban', 'J. K. Rowling', 'venta', 'bueno', '8.50', 1, ''),
    ('El Nombre del Viento', 'Patrick Rothfuss', 'venta', 'excelente', '12.00', 1, ''),
    ('Rayuela', 'Julio Cortázar', 'venta', 'aceptable', '6.00', 1, ''),
    ('Antología Poética', 'Mario Benedetti', 'lectura', '', '0.00', 1, 'A1'),
    ('El Principito', 'Antoine de Saint-Exupéry', 'lectura', '', '0.00', 1, 'B2'),
]


class Command(BaseCommand):
    help = 'Carga el menu de cafeteria y los libros iniciales de Raccoon Cafe.'

    @transaction.atomic
    def handle(self, *args, **options):
        nuevas = {'categorias': 0, 'productos': 0, 'libros': 0}

        categorias = {}
        for nombre, orden in CATEGORIAS:
            categoria, creada = CategoriaMenu.objects.get_or_create(
                nombre=nombre, defaults={'orden': orden}
            )
            categorias[nombre] = categoria
            nuevas['categorias'] += creada

        for nombre, cat, precio, controla, stock, minimo in PRODUCTOS:
            _, creado = ProductoMenu.objects.get_or_create(
                nombre=nombre,
                categoria=categorias[cat],
                defaults={
                    'precio': Decimal(precio),
                    'controla_stock': controla,
                    'stock': stock,
                    'stock_minimo': minimo,
                },
            )
            nuevas['productos'] += creado

        for titulo, autor, tipo, condicion, precio, stock, estante in LIBROS:
            _, creado = Libro.objects.get_or_create(
                titulo=titulo,
                autor=autor,
                defaults={
                    'tipo': tipo,
                    'condicion': condicion,
                    'precio': Decimal(precio),
                    'stock': stock,
                    'estante': estante,
                },
            )
            nuevas['libros'] += creado

        self.stdout.write(self.style.SUCCESS(
            f"Creados: {nuevas['categorias']} categorias, "
            f"{nuevas['productos']} productos, {nuevas['libros']} libros "
            '(los que ya existian se dejaron intactos).'
        ))
