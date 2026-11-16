"""
Comando OPCIONAL: python manage.py cargar_demo

Carga un conjunto de datos de ejemplo (tipos de espacio, espacios,
servicios, clientes, reservas y pagos) para poder mostrar el tablero,
los graficos y el calendario con informacion realista.

No es parte del funcionamiento del sistema: sirve para las pruebas y
las capturas de pantalla. Si no lo ejecutas, el sistema arranca vacio.
"""

import random
from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clientes.models import Cliente
from cuentas.mixins import GRUPO_CLIENTE
from espacios.models import Espacio, Servicio, TipoEspacio
from pagos.models import Pago
from reservas.models import DetalleReserva, Reserva

TIPOS = [
    ('Sala de reuniones', 'Salas cerradas con mesa de trabajo y pantalla.'),
    ('Escritorio flexible', 'Puestos individuales en area compartida.'),
    ('Oficina privada', 'Oficinas cerradas para equipos pequenos.'),
    ('Sala de capacitacion', 'Espacios amplios para talleres y cursos.'),
]

ESPACIOS = [
    ('SAL-01', 'Sala Manglar', 'Sala de reuniones', 'Piso 2, ala norte', 8, '12.00'),
    ('SAL-02', 'Sala Ceibo', 'Sala de reuniones', 'Piso 2, ala sur', 6, '10.00'),
    ('ESC-01', 'Escritorio A1', 'Escritorio flexible', 'Piso 1, area abierta', 1, '3.50'),
    ('ESC-02', 'Escritorio A2', 'Escritorio flexible', 'Piso 1, area abierta', 1, '3.50'),
    ('OFI-01', 'Oficina Guayacan', 'Oficina privada', 'Piso 3, oficina 301', 4, '18.00'),
    ('CAP-01', 'Aula Cacao', 'Sala de capacitacion', 'Piso 3, aula grande', 25, '30.00'),
]

SERVICIOS = [
    ('Proyector HD', 'Proyector con cable HDMI y control remoto.', '8.00'),
    ('Servicio de cafe', 'Cafe, agua y snacks para el grupo.', '2.50'),
    ('Pizarra movil', 'Pizarra de tiza liquida con marcadores.', '4.00'),
    ('Videoconferencia', 'Camara, microfono y soporte tecnico.', '15.00'),
]

CLIENTES = [
    ('0912345678', 'Ana', 'Vera', 'ana.vera@correo.com', '0991112233', 'PERSONAL', None),
    ('0923456789', 'Luis', 'Cedeno', 'luis.cedeno@correo.com', '0992223344', 'EMPRESARIAL', 'Innova SA'),
    ('0934567890', 'Maria', 'Zambrano', 'maria.zambrano@correo.com', '0993334455', 'PERSONAL', None),
    ('0945678901', 'Jorge', 'Bravo', 'jorge.bravo@correo.com', '0994445566', 'EMPRESARIAL', 'Delta Consulting'),
    ('0956789012', 'Camila', 'Rosales', 'camila.rosales@correo.com', '0995556677', 'PERSONAL', None),
]


class Command(BaseCommand):
    help = 'Carga datos de ejemplo para probar el sistema.'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(2026)

        # ---------- Catalogo ----------
        tipos = {}
        for nombre, descripcion in TIPOS:
            tipo, _ = TipoEspacio.objects.get_or_create(
                nombre=nombre, defaults={'descripcion': descripcion}
            )
            tipos[nombre] = tipo

        for codigo, nombre, tipo, ubicacion, capacidad, tarifa in ESPACIOS:
            Espacio.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'tipo_espacio': tipos[tipo],
                    'ubicacion': ubicacion,
                    'capacidad': capacidad,
                    'tarifa_hora': Decimal(tarifa),
                },
            )

        for nombre, descripcion, precio in SERVICIOS:
            Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion, 'precio': Decimal(precio)},
            )

        # ---------- Clientes con cuenta de usuario ----------
        grupo_cliente, _ = Group.objects.get_or_create(name=GRUPO_CLIENTE)
        for cedula, nombres, apellidos, correo, telefono, tipo, empresa in CLIENTES:
            if Cliente.objects.filter(cedula=cedula).exists():
                continue
            usuario_nombre = correo.split('@')[0].replace('.', '')
            usuario, creado = User.objects.get_or_create(
                username=usuario_nombre,
                defaults={'first_name': nombres, 'last_name': apellidos, 'email': correo},
            )
            if creado:
                usuario.set_password('demo12345')
                usuario.save()
                usuario.groups.add(grupo_cliente)
            Cliente.objects.create(
                usuario=usuario,
                cedula=cedula,
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                telefono=telefono,
                tipo_cliente=tipo,
                empresa=empresa,
            )

        # ---------- Reservas de los ultimos 40 dias y proximos 10 ----------
        clientes = list(Cliente.objects.all())
        espacios = list(Espacio.objects.all())
        servicios = list(Servicio.objects.all())
        hoy = timezone.localdate()
        creadas = 0

        for desplazamiento in range(-40, 11):
            dia = hoy + timedelta(days=desplazamiento)
            if dia.weekday() == 6:  # domingo cerrado
                continue
            for _ in range(random.randint(0, 3)):
                espacio = random.choice(espacios)
                inicio = random.choice([8, 9, 10, 13, 15, 17])
                duracion = random.choice([1, 2, 3])
                hora_inicio = time(inicio, 0)
                hora_fin = time(min(inicio + duracion, 22), 0)

                cruce = Reserva.objects.filter(
                    espacio=espacio,
                    fecha=dia,
                    estado__in=Reserva.ESTADOS_VIGENTES,
                    hora_inicio__lt=hora_fin,
                    hora_fin__gt=hora_inicio,
                ).exists()
                if cruce or hora_fin <= hora_inicio:
                    continue

                reserva = Reserva.objects.create(
                    cliente=random.choice(clientes),
                    espacio=espacio,
                    fecha=dia,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    numero_personas=random.randint(1, espacio.capacidad),
                    estado=Reserva.Estado.PENDIENTE,
                )
                creadas += 1

                if random.random() < 0.45:
                    DetalleReserva.objects.create(
                        reserva=reserva,
                        servicio=random.choice(servicios),
                        cantidad=random.randint(1, 2),
                    )

                reserva.refresh_from_db()

                # Las reservas pasadas se pagan y completan; las futuras varian.
                if desplazamiento < 0:
                    Pago.objects.create(
                        reserva=reserva,
                        monto=reserva.total,
                        metodo_pago=random.choice(
                            [m for m, _ in Pago.MetodoPago.choices]
                        ),
                    )
                    Reserva.objects.filter(pk=reserva.pk).update(
                        estado=Reserva.Estado.COMPLETADA
                    )
                elif random.random() < 0.6:
                    Pago.objects.create(
                        reserva=reserva,
                        monto=reserva.total,
                        metodo_pago=Pago.MetodoPago.TRANSFERENCIA,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Datos de ejemplo cargados: {creadas} reservas, '
                f'{len(espacios)} espacios, {len(clientes)} clientes. '
                'Usuarios de prueba con clave demo12345.'
            )
        )
