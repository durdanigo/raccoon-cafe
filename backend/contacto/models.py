"""
Modulo CONTACTO
---------------
Mensajes que los visitantes envian desde el formulario publico del
sitio web. Se guardan en la base de datos para que el equipo los lea
desde el panel de administracion (Django admin o el panel React).
"""

from django.db import models


class Mensaje(models.Model):
    """Un mensaje enviado desde el formulario de contacto."""

    class Asunto(models.TextChoices):
        RESERVA = 'reserva', 'Reserva de sala'
        CAFETERIA = 'cafeteria', 'Cafetería'
        LIBROS = 'libros', 'Libros'
        EVENTO = 'evento', 'Evento o taller'
        OTRO = 'otro', 'Otro'

    id = models.BigAutoField(primary_key=True, db_column='id_mensaje')
    nombre = models.CharField(max_length=100, db_column='nombre')
    correo = models.EmailField(db_column='correo')
    asunto = models.CharField(
        max_length=10, choices=Asunto.choices, default=Asunto.OTRO, db_column='asunto'
    )
    mensaje = models.TextField(db_column='mensaje')
    leido = models.BooleanField(default=False, db_column='leido')
    creado_en = models.DateTimeField(auto_now_add=True, db_column='creado_en')

    class Meta:
        db_table = 'contacto_mensaje'
        ordering = ['-creado_en']
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'

    def __str__(self):
        return f'{self.nombre} — {self.get_asunto_display()}'
