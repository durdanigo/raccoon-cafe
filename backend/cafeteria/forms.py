"""Formularios del modulo CAFETERIA."""

from django import forms

from bookspace_manager.formularios import FormularioTailwindMixin
from cafeteria.models import CategoriaMenu, ProductoMenu


class CategoriaMenuForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = CategoriaMenu
        fields = ['nombre', 'descripcion', 'orden', 'activa']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre


class ProductoMenuForm(FormularioTailwindMixin, forms.ModelForm):
    class Meta:
        model = ProductoMenu
        fields = [
            'categoria',
            'nombre',
            'precio',
            'descripcion',
            'controla_stock',
            'stock',
            'stock_minimo',
            'disponible',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo se ofrecen categorias activas (mas la actual al editar).
        activas = CategoriaMenu.objects.filter(activa=True)
        if self.instance.pk:
            activas = CategoriaMenu.objects.filter(
                activa=True
            ) | CategoriaMenu.objects.filter(pk=self.instance.categoria_id)
        self.fields['categoria'].queryset = activas.distinct()
