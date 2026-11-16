"""
Vistas del modulo PANEL (mejora adicional del taller).

Contiene:
    1. Dashboard con indicadores y graficos (Chart.js).
    2. Calendario de reservas (FullCalendar) con su endpoint JSON.

Los datos se filtran segun el rol: el administrador ve la operacion
completa y el cliente unicamente su propia informacion.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from clientes.models import Cliente
from cuentas.mixins import cliente_de, es_administrador
from espacios.models import Espacio
from pagos.models import Pago
from reservas.models import Reserva

MESES = [
    'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic',
]

COLORES_ESTADO = {
    Reserva.Estado.PENDIENTE: '#F59E0B',
    Reserva.Estado.CONFIRMADA: '#0D9488',
    Reserva.Estado.COMPLETADA: '#334155',
    Reserva.Estado.CANCELADA: '#DC2626',
}


def reservas_visibles(usuario):
    """Reservas que el usuario tiene derecho a ver."""
    registros = Reserva.objects.select_related('cliente', 'espacio')
    if es_administrador(usuario):
        return registros
    cliente = cliente_de(usuario)
    return registros.filter(cliente=cliente) if cliente else registros.none()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/dashboard.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user
        hoy = timezone.localdate()
        inicio_mes = hoy.replace(day=1)
        admin = es_administrador(usuario)

        reservas = reservas_visibles(usuario)
        pagos = Pago.objects.filter(estado=Pago.Estado.CONFIRMADO)
        if not admin:
            cliente = cliente_de(usuario)
            pagos = pagos.filter(reserva__cliente=cliente) if cliente else pagos.none()

        # ---------------- Indicadores ----------------
        contexto['reservas_hoy'] = reservas.filter(fecha=hoy).count()
        contexto['reservas_mes'] = reservas.filter(
            fecha__gte=inicio_mes, fecha__lte=hoy
        ).count()
        contexto['ingresos_mes'] = pagos.filter(
            fecha_pago__date__gte=inicio_mes
        ).aggregate(suma=Sum('monto'))['suma'] or Decimal('0.00')
        contexto['reservas_pendientes'] = reservas.filter(
            estado=Reserva.Estado.PENDIENTE
        ).count()
        contexto['espacios_disponibles'] = Espacio.objects.filter(
            estado=Espacio.Estado.DISPONIBLE
        ).count()
        contexto['total_espacios'] = Espacio.objects.count()
        contexto['total_clientes'] = Cliente.objects.filter(activo=True).count()

        # ---------------- Grafico 1: reservas de los ultimos 7 dias ----------------
        etiquetas_dias, valores_dias = [], []
        for retroceso in range(6, -1, -1):
            dia = hoy - timedelta(days=retroceso)
            etiquetas_dias.append(dia.strftime('%d/%m'))
            valores_dias.append(reservas.filter(fecha=dia).count())

        # ---------------- Grafico 2: espacios mas reservados ----------------
        mas_reservados = (
            reservas.exclude(estado=Reserva.Estado.CANCELADA)
            .values('espacio__codigo', 'espacio__nombre')
            .annotate(total=Count('id_reserva'))
            .order_by('-total')[:5]
        )
        etiquetas_espacios = [
            f"{fila['espacio__codigo']} - {fila['espacio__nombre']}"
            for fila in mas_reservados
        ]
        valores_espacios = [fila['total'] for fila in mas_reservados]

        # ---------------- Grafico 3: ingresos de los ultimos 6 meses ----------------
        primer_mes = (inicio_mes - timedelta(days=150)).replace(day=1)
        ingresos_por_mes = (
            pagos.filter(fecha_pago__date__gte=primer_mes)
            .annotate(mes=TruncMonth('fecha_pago'))
            .values('mes')
            .annotate(total=Sum('monto'))
            .order_by('mes')
        )
        mapa_ingresos = {}
        for fila in ingresos_por_mes:
            momento = fila['mes']
            clave = (momento.year, momento.month)
            mapa_ingresos[clave] = float(fila['total'] or 0)

        etiquetas_meses, valores_meses = [], []
        anio, mes = primer_mes.year, primer_mes.month
        for _ in range(6):
            etiquetas_meses.append(f'{MESES[mes - 1]} {anio}')
            valores_meses.append(mapa_ingresos.get((anio, mes), 0))
            mes += 1
            if mes > 12:
                mes, anio = 1, anio + 1

        # ---------------- Grafico 4: distribucion por estado ----------------
        por_estado = reservas.values('estado').annotate(total=Count('id_reserva'))
        mapa_estados = {fila['estado']: fila['total'] for fila in por_estado}
        etiquetas_estados = [texto for _, texto in Reserva.Estado.choices]
        valores_estados = [
            mapa_estados.get(valor, 0) for valor, _ in Reserva.Estado.choices
        ]
        colores_estados = [
            COLORES_ESTADO[valor] for valor, _ in Reserva.Estado.choices
        ]

        # Se entrega como diccionario y la plantilla lo serializa con
        # el filtro json_script (evita problemas de escapado en el HTML).
        contexto['datos_graficos'] = {
            'dias': {'etiquetas': etiquetas_dias, 'valores': valores_dias},
            'espacios': {
                'etiquetas': etiquetas_espacios,
                'valores': valores_espacios,
            },
            'ingresos': {
                'etiquetas': etiquetas_meses,
                'valores': valores_meses,
            },
            'estados': {
                'etiquetas': etiquetas_estados,
                'valores': valores_estados,
                'colores': colores_estados,
            },
        }

        contexto['proximas_reservas'] = (
            reservas.filter(fecha__gte=hoy)
            .exclude(estado=Reserva.Estado.CANCELADA)
            .order_by('fecha', 'hora_inicio')[:6]
        )
        return contexto


class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/calendario.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['estados'] = [
            (valor, texto, COLORES_ESTADO[valor])
            for valor, texto in Reserva.Estado.choices
        ]
        return contexto


class EventosCalendarioView(LoginRequiredMixin, View):
    """Entrega las reservas en el formato de eventos que espera FullCalendar."""

    def get(self, request):
        registros = reservas_visibles(request.user)

        inicio = request.GET.get('start')
        fin = request.GET.get('end')
        if inicio and fin:
            registros = registros.filter(
                fecha__gte=self._a_fecha(inicio), fecha__lte=self._a_fecha(fin)
            )

        eventos = []
        for reserva in registros:
            eventos.append(
                {
                    'id': reserva.pk,
                    'title': f'{reserva.espacio.codigo} - {reserva.cliente.nombre_completo}',
                    'start': f'{reserva.fecha.isoformat()}T{reserva.hora_inicio.isoformat()}',
                    'end': f'{reserva.fecha.isoformat()}T{reserva.hora_fin.isoformat()}',
                    'backgroundColor': COLORES_ESTADO.get(reserva.estado, '#0D9488'),
                    'borderColor': COLORES_ESTADO.get(reserva.estado, '#0D9488'),
                    'url': f'/reservas/{reserva.pk}/',
                    'extendedProps': {
                        'codigo': reserva.codigo,
                        'estado': reserva.get_estado_display(),
                        'total': str(reserva.total),
                    },
                }
            )
        return JsonResponse(eventos, safe=False)

    @staticmethod
    def _a_fecha(texto):
        try:
            return datetime.fromisoformat(texto.replace('Z', '+00:00')).date()
        except ValueError:
            return date.today()
