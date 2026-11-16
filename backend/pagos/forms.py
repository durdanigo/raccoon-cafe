"""Formularios del modulo PAGOS."""

from django import forms

from bookspace_manager.formularios import FormularioTailwindMixin
from pagos.models import Pago
from reservas.models import Reserva


class PagoForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['reserva', 'monto', 'metodo_pago', 'estado', 'referencia']
        widgets = {
            'monto': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'referencia': forms.TextInput(
                attrs={'placeholder': 'N. de comprobante o transaccion'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se pueden pagar reservas que no esten canceladas.
        self.fields['reserva'].queryset = (
            Reserva.objects.exclude(estado=Reserva.Estado.CANCELADA)
            .select_related('cliente', 'espacio')
        )
