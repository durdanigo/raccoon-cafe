"""
Vistas de la API REST.

Publica los datos del sistema Raccoon Cafe en formato JSON para
que sean consumidos por la aplicacion movil desarrollada en React
Native. Los catalogos son de solo lectura; el modulo de reservas
permite ademas registrar nuevas reservas desde el dispositivo.
"""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from api.permissions import EsAdministrador, EsAdministradorOSoloLectura

from api.serializers import (
    CategoriaMenuSerializer,
    ClienteSerializer,
    EspacioSerializer,
    LibroSerializer,
    LoginSerializer,
    MensajeAdminSerializer,
    MensajePublicoSerializer,
    PagoSerializer,
    ProductoMenuSerializer,
    ReservaSerializer,
    ServicioSerializer,
    TipoEspacioSerializer,
)
from cafeteria.models import CategoriaMenu, ProductoMenu
from clientes.models import Cliente
from contacto.models import Mensaje
from cuentas.mixins import es_administrador
from espacios.models import Espacio, Servicio, TipoEspacio
from libreria.models import Libro
from pagos.models import Pago
from reservas.models import Reserva


# ============================================================
# CATALOGO
# ============================================================
class TipoEspacioViewSet(viewsets.ReadOnlyModelViewSet):
    """Tipos de espacio del coworking."""

    serializer_class = TipoEspacioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        registros = TipoEspacio.objects.all()
        if self.request.query_params.get('activo') == 'true':
            registros = registros.filter(activo=True)
        return registros


class EspacioViewSet(viewsets.ReadOnlyModelViewSet):
    """Espacios reservables: salas, oficinas y escritorios."""

    serializer_class = EspacioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        registros = Espacio.objects.select_related('tipo_espacio')

        estado = self.request.query_params.get('estado')
        if estado:
            registros = registros.filter(estado=estado.upper())

        tipo = self.request.query_params.get('tipo')
        if tipo:
            registros = registros.filter(tipo_espacio_id=tipo)

        busqueda = self.request.query_params.get('q')
        if busqueda:
            registros = registros.filter(nombre__icontains=busqueda)

        return registros


class ServicioViewSet(viewsets.ReadOnlyModelViewSet):
    """Servicios adicionales que se agregan a una reserva."""

    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        registros = Servicio.objects.all()
        if self.request.query_params.get('activo') == 'true':
            registros = registros.filter(activo=True)
        return registros


# ============================================================
# CAFETERIA Y LIBRERIA (solo lectura)
# ============================================================
def _como_booleano(valor):
    """Convierte 'true'/'false' del query string; None si no es ninguno."""
    valor = (valor or '').lower()
    if valor in ('true', '1'):
        return True
    if valor in ('false', '0'):
        return False
    return None


class CategoriaMenuViewSet(viewsets.ReadOnlyModelViewSet):
    """Categorias de la carta de la cafeteria."""

    serializer_class = CategoriaMenuSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        registros = CategoriaMenu.objects.all()
        if self.request.query_params.get('activa') == 'true':
            registros = registros.filter(activa=True)
        return registros


class ProductoMenuViewSet(viewsets.ModelViewSet):
    """Productos de la carta. Filtros: ?categoria=<id>&disponible=true|false

    Cualquiera puede consultarlos; crear, editar o borrar exige el token
    de un administrador (cabecera `Authorization: Token <token>`).
    """

    serializer_class = ProductoMenuSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [EsAdministradorOSoloLectura]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        registros = ProductoMenu.objects.select_related('categoria')

        categoria = self.request.query_params.get('categoria')
        if categoria and categoria.isdigit():
            registros = registros.filter(categoria_id=categoria)

        disponible = _como_booleano(self.request.query_params.get('disponible'))
        if disponible is not None:
            registros = registros.filter(disponible=disponible)

        return registros


class LibroViewSet(viewsets.ModelViewSet):
    """Libros. Filtros: ?tipo=venta|lectura&disponible=true|false

    Lectura publica; escritura solo para administradores con token.
    """

    serializer_class = LibroSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [EsAdministradorOSoloLectura]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        registros = Libro.objects.all()

        tipo = self.request.query_params.get('tipo')
        if tipo in Libro.Tipo.values:
            registros = registros.filter(tipo=tipo)

        disponible = _como_booleano(self.request.query_params.get('disponible'))
        if disponible is not None:
            registros = registros.filter(disponible=disponible)

        return registros


# ============================================================
# CONTACTO
# ============================================================
class MensajeViewSet(viewsets.ModelViewSet):
    """Mensajes del formulario de contacto.

    - POST  /api/contacto/      publico, con limite de envios por IP.
    - GET / PATCH / DELETE      solo administradores (token).
    """

    queryset = Mensaje.objects.all()
    authentication_classes = [TokenAuthentication]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    throttle_scope = 'contacto'

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [EsAdministrador()]

    def get_throttles(self):
        # El limite solo protege el envio publico, no el panel de admin.
        if self.action == 'create':
            return [ScopedRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == 'create':
            return MensajePublicoSerializer
        return MensajeAdminSerializer

    def get_queryset(self):
        registros = Mensaje.objects.all()
        leido = _como_booleano(self.request.query_params.get('leido'))
        if leido is not None:
            registros = registros.filter(leido=leido)
        return registros

    def create(self, request, *args, **kwargs):
        serializador = self.get_serializer(data=request.data)
        serializador.is_valid(raise_exception=True)

        # Honeypot: un bot llena el campo oculto; respondemos igual de
        # amable para no darle pistas, pero no guardamos nada.
        if serializador.validated_data.get('website'):
            return Response({'detalle': 'Mensaje recibido.'}, status=status.HTTP_201_CREATED)

        serializador.validated_data.pop('website', None)
        serializador.save()
        return Response(
            {'detalle': 'Mensaje recibido. Te responderemos pronto.'},
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# CLIENTES
# ============================================================
class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    """Clientes registrados en el coworking."""

    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        registros = Cliente.objects.all().order_by('apellidos', 'nombres')

        busqueda = self.request.query_params.get('q')
        if busqueda:
            registros = registros.filter(apellidos__icontains=busqueda)

        return registros


# ============================================================
# RESERVAS
# ============================================================
class ReservaViewSet(viewsets.ModelViewSet):
    """Reservas del coworking.

    Ademas de consultarlas, permite registrar una nueva reserva desde
    la aplicacion movil. Las reglas de negocio (horario de atencion,
    capacidad del espacio y cruces de horario) se validan igual que en
    el sistema web.
    """

    serializer_class = ReservaSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        registros = Reserva.objects.select_related('cliente', 'espacio')

        estado = self.request.query_params.get('estado')
        if estado:
            registros = registros.filter(estado=estado.upper())

        fecha = self.request.query_params.get('fecha')
        if fecha:
            registros = registros.filter(fecha=fecha)

        cliente = self.request.query_params.get('cliente')
        if cliente:
            registros = registros.filter(cliente_id=cliente)

        if self.request.query_params.get('proximas') == 'true':
            registros = registros.filter(
                fecha__gte=timezone.localdate()
            ).exclude(estado=Reserva.Estado.CANCELADA).order_by('fecha', 'hora_inicio')

        return registros


class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    """Pagos registrados sobre las reservas."""

    serializer_class = PagoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        registros = Pago.objects.select_related('reserva', 'reserva__cliente')

        metodo = self.request.query_params.get('metodo')
        if metodo:
            registros = registros.filter(metodo_pago=metodo.upper())

        reserva = self.request.query_params.get('reserva')
        if reserva:
            registros = registros.filter(reserva_id=reserva)

        return registros


# ============================================================
# INDICADORES DEL TABLERO
# ============================================================
class DashboardAPIView(APIView):
    """Entrega los mismos indicadores que muestra el tablero web."""

    permission_classes = [AllowAny]

    def get(self, request):
        hoy = timezone.localdate()
        inicio_mes = hoy.replace(day=1)

        reservas = Reserva.objects.all()
        pagos_confirmados = Pago.objects.filter(estado=Pago.Estado.CONFIRMADO)

        ingresos = pagos_confirmados.filter(
            fecha_pago__date__gte=inicio_mes
        ).aggregate(suma=Sum('monto'))['suma'] or Decimal('0.00')

        # Reservas de los ultimos 7 dias
        etiquetas_dias, valores_dias = [], []
        for retroceso in range(6, -1, -1):
            dia = hoy - timedelta(days=retroceso)
            etiquetas_dias.append(dia.strftime('%d/%m'))
            valores_dias.append(reservas.filter(fecha=dia).count())

        # Espacios mas reservados
        mas_reservados = (
            reservas.exclude(estado=Reserva.Estado.CANCELADA)
            .values('espacio__codigo', 'espacio__nombre')
            .annotate(total=Count('id_reserva'))
            .order_by('-total')[:5]
        )

        # Distribucion por estado
        por_estado = {
            fila['estado']: fila['total']
            for fila in reservas.values('estado').annotate(total=Count('id_reserva'))
        }

        return Response({
            'reservas_hoy': reservas.filter(fecha=hoy).count(),
            'reservas_mes': reservas.filter(
                fecha__gte=inicio_mes, fecha__lte=hoy
            ).count(),
            'ingresos_mes': str(ingresos),
            'reservas_pendientes': reservas.filter(
                estado=Reserva.Estado.PENDIENTE
            ).count(),
            'espacios_disponibles': Espacio.objects.filter(
                estado=Espacio.Estado.DISPONIBLE
            ).count(),
            'total_espacios': Espacio.objects.count(),
            'total_clientes': Cliente.objects.filter(activo=True).count(),
            'total_reservas': reservas.count(),
            'reservas_por_dia': {
                'etiquetas': etiquetas_dias,
                'valores': valores_dias,
            },
            'espacios_mas_reservados': [
                {
                    'codigo': fila['espacio__codigo'],
                    'nombre': fila['espacio__nombre'],
                    'total': fila['total'],
                }
                for fila in mas_reservados
            ],
            'reservas_por_estado': [
                {
                    'estado': valor,
                    'texto': texto,
                    'total': por_estado.get(valor, 0),
                }
                for valor, texto in Reserva.Estado.choices
            ],
        })


# ============================================================
# AUTENTICACION
# ============================================================
class LoginAPIView(APIView):
    """Valida las credenciales enviadas desde la aplicacion movil."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializador = LoginSerializer(data=request.data)
        serializador.is_valid(raise_exception=True)

        usuario = serializador.validated_data['usuario_autenticado']
        perfil = getattr(usuario, 'cliente_asociado', None)
        # Token para las llamadas autenticadas del panel web de administracion.
        token, _ = Token.objects.get_or_create(user=usuario)

        return Response({
            'autenticado': True,
            'id': usuario.id,
            'usuario': usuario.username,
            'nombre': usuario.get_full_name() or usuario.username,
            'correo': usuario.email,
            'rol': 'Administrador' if es_administrador(usuario) else 'Cliente',
            'id_cliente': perfil.pk if perfil else None,
            'token': token.key,
        })


# ============================================================
# RAIZ DE LA API
# ============================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def raiz_api(request):
    """Lista los servicios disponibles en la API."""
    base = request.build_absolute_uri('/api/')
    return Response({
        'sistema': 'Raccoon Café',
        'descripcion': 'API REST de Raccoon Café: salas, cafetería y librería',
        'version': '1.0',
        'servicios': {
            'categorias_menu': base + 'categorias-menu/',
            'menu': base + 'menu/',
            'libros': base + 'libros/',
            'contacto': base + 'contacto/',
            'tipos_espacio': base + 'tipos-espacio/',
            'espacios': base + 'espacios/',
            'servicios': base + 'servicios/',
            'clientes': base + 'clientes/',
            'reservas': base + 'reservas/',
            'pagos': base + 'pagos/',
            'dashboard': base + 'dashboard/',
            'login': base + 'login/',
        },
    }, status=status.HTTP_200_OK)
