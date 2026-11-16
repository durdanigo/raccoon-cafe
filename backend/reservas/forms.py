"""Formularios del modulo RESERVAS."""

from django import forms

from bookspace_manager.formularios import FormularioTailwindMixin
from clientes.models import Cliente
from espacios.models import Espacio, Servicio
from reservas.models import DetalleReserva, Reserva


class ReservaForm(FormularioTailwindMixin, forms.ModelForm):
    """Formulario de reserva.

    Si el usuario es un cliente, el campo 'cliente' se oculta y se
    asigna automaticamente en la vista; ademas no puede cambiar el estado.
    """

    class Meta:
        model = Reserva
        fields = [
            'cliente',
            'espacio',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'numero_personas',
            'estado',
            'observaciones',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, es_administrador=True, cliente_actual=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.es_administrador = es_administrador
        self.cliente_actual = cliente_actual

        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        self.fields['espacio'].queryset = Espacio.objects.filter(
            estado=Espacio.Estado.DISPONIBLE
        ).select_related('tipo_espacio')

        if not es_administrador:
            # El cliente no elige a nombre de quien reserva ni el estado.
            del self.fields['cliente']
            del self.fields['estado']

    def clean(self):
        datos = super().clean()
        # Se completa la instancia para poder ejecutar las validaciones
        # de negocio definidas en Reserva.clean().
        if not self.es_administrador and self.cliente_actual:
            self.instance.cliente = self.cliente_actual
        return datos


class DetalleReservaForm(FormularioTailwindMixin, forms.ModelForm):
    """Agrega un servicio adicional a una reserva existente."""

    class Meta:
        model = DetalleReserva
        fields = ['servicio', 'cantidad']

    def __init__(self, *args, reserva=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.reserva = reserva
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True)

    def clean_servicio(self):
        servicio = self.cleaned_data['servicio']
        if self.reserva and DetalleReserva.objects.filter(
            reserva=self.reserva, servicio=servicio
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                'Ese servicio ya fue agregado a la reserva; edita la cantidad.'
            )
        return servicio
