# Escrita a mano con el mismo formato que genera Django 6.0.7.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(db_column='id_mensaje', primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='nombre', max_length=100)),
                ('correo', models.EmailField(db_column='correo', max_length=254)),
                ('asunto', models.CharField(choices=[('reserva', 'Reserva de sala'), ('cafeteria', 'Cafetería'), ('libros', 'Libros'), ('evento', 'Evento o taller'), ('otro', 'Otro')], db_column='asunto', default='otro', max_length=10)),
                ('mensaje', models.TextField(db_column='mensaje')),
                ('leido', models.BooleanField(db_column='leido', default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True, db_column='creado_en')),
            ],
            options={
                'verbose_name': 'Mensaje de contacto',
                'verbose_name_plural': 'Mensajes de contacto',
                'db_table': 'contacto_mensaje',
                'ordering': ['-creado_en'],
            },
        ),
    ]
