"""Formularios del modulo LIBRERIA."""

from django import forms

from bookspace_manager.formularios import FormularioTailwindMixin
from libreria.models import Libro


class LibroForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = Libro
        fields = [
            'titulo',
            'autor',
            'genero',
            'tipo',
            'condicion',
            'precio',
            'stock',
            'estante',
            'disponible',
        ]
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'estante': forms.TextInput(attrs={'placeholder': 'Ej: A1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Para los libros de lectura el precio se fuerza a 0 en clean(),
        # asi que no tiene sentido obligar a escribirlo.
        self.fields['precio'].required = False
        self.fields['condicion'].required = False

    def clean_estante(self):
        return self.cleaned_data['estante'].strip().upper()
