"""Formularios del modulo CUENTAS (autenticacion y registro)."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from bookspace_manager.formularios import FormularioTailwindMixin
from clientes.models import Cliente, validador_cedula


class LoginForm(FormularioTailwindMixin, AuthenticationForm):
    """Inicio de sesion con estilos del sistema."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Usuario'
        self.fields['password'].widget.attrs['placeholder'] = 'Contrasena'


class RegistroClienteForm(FormularioTailwindMixin, UserCreationForm):
    """Crea la cuenta de usuario y el perfil de cliente en un solo paso."""

    cedula = forms.CharField(
        max_length=10, validators=[validador_cedula], label='Cedula'
    )
    nombres = forms.CharField(max_length=80, label='Nombres')
    apellidos = forms.CharField(max_length=80, label='Apellidos')
    correo = forms.EmailField(label='Correo electronico')
    telefono = forms.CharField(max_length=15, label='Telefono')
    tipo_cliente = forms.ChoiceField(
        choices=Cliente.TipoCliente.choices, label='Tipo de cliente'
    )
    empresa = forms.CharField(max_length=120, required=False, label='Empresa')

    class Meta:
        model = User
        fields = ['username']

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']
        if Cliente.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError('Ya existe un cliente con esa cedula.')
        return cedula

    def clean_correo(self):
        correo = self.cleaned_data['correo'].lower()
        if Cliente.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Ya existe un cliente con ese correo.')
        return correo

    def clean(self):
        datos = super().clean()
        if (
            datos.get('tipo_cliente') == Cliente.TipoCliente.EMPRESARIAL
            and not datos.get('empresa')
        ):
            self.add_error('empresa', 'Indica el nombre de la empresa.')
        return datos

    @transaction.atomic
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.first_name = self.cleaned_data['nombres']
        usuario.last_name = self.cleaned_data['apellidos']
        usuario.email = self.cleaned_data['correo']
        usuario.save()

        Cliente.objects.create(
            usuario=usuario,
            cedula=self.cleaned_data['cedula'],
            nombres=self.cleaned_data['nombres'],
            apellidos=self.cleaned_data['apellidos'],
            correo=self.cleaned_data['correo'],
            telefono=self.cleaned_data['telefono'],
            tipo_cliente=self.cleaned_data['tipo_cliente'],
            empresa=self.cleaned_data.get('empresa') or None,
        )
        return usuario
