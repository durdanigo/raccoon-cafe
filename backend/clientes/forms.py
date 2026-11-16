"""Formularios del modulo CLIENTES."""

from django import forms

from bookspace_manager.formularios import FormularioTailwindMixin
from clientes.models import Cliente


class ClienteForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'cedula',
            'nombres',
            'apellidos',
            'correo',
            'telefono',
            'tipo_cliente',
            'empresa',
            'activo',
        ]
        widgets = {
            'cedula': forms.TextInput(attrs={'placeholder': '10 digitos'}),
            'telefono': forms.TextInput(attrs={'placeholder': '09XXXXXXXX'}),
        }

    def clean(self):
        datos = super().clean()
        if (
            datos.get('tipo_cliente') == Cliente.TipoCliente.EMPRESARIAL
            and not datos.get('empresa')
        ):
            self.add_error(
                'empresa',
                'Un cliente empresarial debe indicar el nombre de la empresa.',
            )
        return datos
