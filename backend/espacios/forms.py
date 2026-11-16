"""Formularios del modulo ESPACIOS."""

from django import forms

from bookspace_manager.formularios import FormularioTailwindMixin
from espacios.models import Espacio, Servicio, TipoEspacio


class TipoEspacioForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = TipoEspacio
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre


class EspacioForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = Espacio
        fields = [
            'tipo_espacio',
            'codigo',
            'nombre',
            'ubicacion',
            'capacidad',
            'tarifa_hora',
            'estado',
            'descripcion',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej: SAL-01'}),
            'tarifa_hora': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se ofrecen tipos de espacio activos.
        self.fields['tipo_espacio'].queryset = TipoEspacio.objects.filter(activo=True)

    def clean_codigo(self):
        return self.cleaned_data['codigo'].strip().upper()


class ServicioForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
