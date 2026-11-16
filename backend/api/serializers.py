"""
Serializadores de la API REST.

Convierten los modelos de Django a JSON para que la aplicacion movil
pueda consumirlos. Se incluyen campos calculados y las descripciones
legibles de los campos con opciones (get_..._display), de modo que la
app no tenga que duplicar esa logica.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from cafeteria.models import CategoriaMenu, ProductoMenu
from clientes.models import Cliente
from espacios.models import Espacio, Servicio, TipoEspacio
from libreria.models import Libro
from pagos.models import Pago
from reservas.models import DetalleReserva, Reserva


# ============================================================
# CATALOGO
# ============================================================
class TipoEspacioSerializer(serializers.ModelSerializer):
    total_espacios = serializers.IntegerField(
        source='espacios_del_tipo.count', read_only=True
    )

    class Meta:
        model = TipoEspacio
        fields = ['id_tipo_espacio', 'nombre', 'descripcion', 'activo', 'total_espacios']


class EspacioSerializer(serializers.ModelSerializer):
    tipo_espacio_nombre = serializers.CharField(
        source='tipo_espacio.nombre', read_only=True
    )
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Espacio
        fields = [
            'id_espacio',
            'codigo',
            'nombre',
            'tipo_espacio',
            'tipo_espacio_nombre',
            'ubicacion',
            'capacidad',
            'tarifa_hora',
            'estado',
            'estado_texto',
            'descripcion',
        ]


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id_servicio', 'nombre', 'descripcion', 'precio', 'activo']


# ============================================================
# CAFETERIA Y LIBRERIA
# ============================================================
class CategoriaMenuSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(source='productos.count', read_only=True)

    class Meta:
        model = CategoriaMenu
        fields = ['id', 'nombre', 'descripcion', 'orden', 'activa', 'total_productos']


class ProductoMenuSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    bajo_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductoMenu
        fields = [
            'id',
            'categoria',
            'categoria_nombre',
            'nombre',
            'descripcion',
            'precio',
            'controla_stock',
            'stock',
            'stock_minimo',
            'bajo_stock',
            'disponible',
        ]


class LibroSerializer(serializers.ModelSerializer):
    tipo_texto = serializers.CharField(source='get_tipo_display', read_only=True)
    condicion_texto = serializers.CharField(source='get_condicion_display', read_only=True)
    en_venta = serializers.BooleanField(read_only=True)

    class Meta:
        model = Libro
        fields = [
            'id',
            'titulo',
            'autor',
            'genero',
            'tipo',
            'tipo_texto',
            'condicion',
            'condicion_texto',
            'precio',
            'stock',
            'estante',
            'en_venta',
            'disponible',
        ]


# ============================================================
# CLIENTES
# ============================================================
class ClienteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    tipo_cliente_texto = serializers.CharField(
        source='get_tipo_cliente_display', read_only=True
    )
    total_reservas = serializers.IntegerField(
        source='reservas_del_cliente.count', read_only=True
    )

    class Meta:
        model = Cliente
        fields = [
            'id_cliente',
            'cedula',
            'nombres',
            'apellidos',
            'nombre_completo',
            'correo',
            'telefono',
            'empresa',
            'tipo_cliente',
            'tipo_cliente_texto',
            'activo',
            'total_reservas',
        ]


# ============================================================
# RESERVAS
# ============================================================
class DetalleReservaSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)

    class Meta:
        model = DetalleReserva
        fields = [
            'id_detalle_reserva',
            'servicio',
            'servicio_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]


class ReservaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(
        source='cliente.nombre_completo', read_only=True
    )
    espacio_codigo = serializers.CharField(source='espacio.codigo', read_only=True)
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)
    horas = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    total_pagado = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    saldo_pendiente = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    detalles = DetalleReservaSerializer(
        source='detalles_de_reserva', many=True, read_only=True
    )

    class Meta:
        model = Reserva
        fields = [
            'id_reserva',
            'codigo',
            'cliente',
            'cliente_nombre',
            'espacio',
            'espacio_codigo',
            'espacio_nombre',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'horas',
            'numero_personas',
            'estado',
            'estado_texto',
            'observaciones',
            'subtotal_espacio',
            'subtotal_servicios',
            'total',
            'total_pagado',
            'saldo_pendiente',
            'detalles',
        ]
        read_only_fields = [
            'codigo',
            'subtotal_espacio',
            'subtotal_servicios',
            'total',
        ]

    def validate(self, datos):
        """Aplica las reglas de negocio definidas en el modelo.

        El metodo clean() de Reserva valida el horario de atencion, la
        capacidad del espacio y los cruces de horario. Se invoca aqui
        para que la API rechace los mismos casos que el sistema web.
        """
        from django.core.exceptions import ValidationError as ErrorDeModelo

        instancia = Reserva(**datos)
        if self.instance:
            instancia.pk = self.instance.pk
            instancia.id_reserva = self.instance.pk

        try:
            instancia.clean()
        except ErrorDeModelo as error:
            raise serializers.ValidationError(error.message_dict)

        return datos


class PagoSerializer(serializers.ModelSerializer):
    reserva_codigo = serializers.CharField(source='reserva.codigo', read_only=True)
    cliente_nombre = serializers.CharField(
        source='reserva.cliente.nombre_completo', read_only=True
    )
    metodo_pago_texto = serializers.CharField(
        source='get_metodo_pago_display', read_only=True
    )
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pago
        fields = [
            'id_pago',
            'reserva',
            'reserva_codigo',
            'cliente_nombre',
            'fecha_pago',
            'monto',
            'metodo_pago',
            'metodo_pago_texto',
            'estado',
            'estado_texto',
            'referencia',
        ]


# ============================================================
# AUTENTICACION
# ============================================================
class LoginSerializer(serializers.Serializer):
    """Valida las credenciales enviadas por la aplicacion movil."""

    usuario = serializers.CharField()
    clave = serializers.CharField(write_only=True)

    def validate(self, datos):
        usuario = authenticate(
            username=datos['usuario'].strip(),
            password=datos['clave'],
        )
        if usuario is None:
            raise serializers.ValidationError(
                {'detalle': 'Usuario o contrasena incorrectos.'}
            )
        if not usuario.is_active:
            raise serializers.ValidationError(
                {'detalle': 'La cuenta se encuentra inactiva.'}
            )
        datos['usuario_autenticado'] = usuario
        return datos
