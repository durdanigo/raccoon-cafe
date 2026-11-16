"""
Estilos compartidos para los formularios del sistema.

Django genera los widgets HTML sin clases CSS. Este mixin recorre los
campos del formulario y les aplica las clases utilitarias de Tailwind,
de modo que todos los formularios del sistema se vean igual sin repetir
la configuracion en cada ModelForm.
"""

from django import forms

CLASES_CAMPO = (
    'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm '
    'text-slate-800 placeholder-slate-400 shadow-sm transition '
    'focus:border-marca-500 focus:outline-none focus:ring-2 focus:ring-marca-200'
)

CLASES_CHECKBOX = (
    'h-4 w-4 rounded border-slate-300 text-marca-600 '
    'focus:ring-2 focus:ring-marca-200'
)

CLASES_SELECT = CLASES_CAMPO + ' pr-8'

CLASES_TEXTAREA = CLASES_CAMPO + ' min-h-[90px]'


class FormularioTailwindMixin:
    """Aplica las clases de Tailwind a todos los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = CLASES_CHECKBOX
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = CLASES_TEXTAREA
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = CLASES_SELECT
            else:
                widget.attrs['class'] = CLASES_CAMPO

            if isinstance(widget, forms.DateInput):
                widget.input_type = 'date'
            if isinstance(widget, forms.TimeInput):
                widget.input_type = 'time'
