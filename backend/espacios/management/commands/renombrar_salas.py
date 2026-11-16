"""
Comando: python manage.py renombrar_salas [--aplicar]

Convierte los espacios existentes en las seis salas de Raccoon Cafe
ACTUALIZANDO los registros (no crea espacios ni borra ninguno), de modo
que las reservas siguen apuntando a la misma fila.

Por defecto es una simulacion: muestra que cambiaria y no escribe nada.
Con --aplicar guarda los cambios.

Seguridad:
    - Si en la base no hay exactamente 6 espacios, el comando se detiene,
      lista los que hay y NO toca nada (el mapeo lo decide una persona).
    - Los espacios se emparejan por orden de creacion (id_espacio).
    - Se conserva el codigo (SAL-01, etc.): es unico y aparece en reservas.
    - Se crean los tipos de espacio que falten (Co-work, Encuentro,
      Taller, Social); los tipos antiguos no se borran.
    - El modelo Espacio solo tiene `capacidad` (un unico numero, no
      minimo/maximo): se usa el MAXIMO de cada rango.
    - Las reservas ya guardadas conservan sus totales; no se recalculan.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from espacios.models import Espacio, TipoEspacio

# (nombre, tipo, capacidad maxima del rango, tarifa por hora)
SALAS = [
    ('Co-work Bosque', 'Co-work', 10, '12.00'),
    ('Co-work Roble', 'Co-work', 10, '12.00'),
    ('Encuentro Nogal', 'Encuentro', 12, '18.00'),
    ('Encuentro Cedro', 'Encuentro', 12, '18.00'),
    ('Taller Raccoon', 'Taller', 20, '25.00'),
    ('Sala Social Luna', 'Social', 25, '32.00'),
]


class Command(BaseCommand):
    help = 'Renombra los 6 espacios existentes a las salas de Raccoon Cafe.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--aplicar',
            action='store_true',
            help='Guarda los cambios. Sin esta opcion solo se simula.',
        )

    def handle(self, *args, **options):
        espacios = list(Espacio.objects.select_related('tipo_espacio').order_by('id_espacio'))

        if len(espacios) != len(SALAS):
            listado = '\n'.join(
                f'  id={e.pk} codigo={e.codigo} nombre="{e.nombre}" '
                f'capacidad={e.capacidad} tarifa={e.tarifa_hora}'
                for e in espacios
            )
            raise CommandError(
                f'Se esperaban {len(SALAS)} espacios y hay {len(espacios)}. '
                f'No se modifico nada. Espacios actuales:\n{listado}'
            )

        aplicar = options['aplicar']
        self.stdout.write('Simulacion (usa --aplicar para guardar):' if not aplicar else 'Aplicando:')

        with transaction.atomic():
            tipos = {}
            for _, tipo, _, _ in SALAS:
                if tipo in tipos:
                    continue
                if aplicar:
                    tipos[tipo], _ = TipoEspacio.objects.get_or_create(nombre=tipo)
                else:
                    tipos[tipo] = TipoEspacio.objects.filter(nombre=tipo).first()

            for espacio, (nombre, tipo, capacidad, tarifa) in zip(espacios, SALAS):
                self.stdout.write(
                    f'  [{espacio.codigo}] "{espacio.nombre}" '
                    f'({espacio.tipo_espacio.nombre}, cap {espacio.capacidad}, '
                    f'${espacio.tarifa_hora}) -> "{nombre}" '
                    f'({tipo}, cap {capacidad}, ${tarifa})'
                )
                if aplicar:
                    espacio.nombre = nombre
                    espacio.tipo_espacio = tipos[tipo]
                    espacio.capacidad = capacidad
                    espacio.tarifa_hora = Decimal(tarifa)
                    espacio.save(
                        update_fields=['nombre', 'tipo_espacio', 'capacidad', 'tarifa_hora']
                    )

        if aplicar:
            self.stdout.write(self.style.SUCCESS('Salas actualizadas.'))
        else:
            self.stdout.write(self.style.WARNING('No se guardo nada (simulacion).'))
