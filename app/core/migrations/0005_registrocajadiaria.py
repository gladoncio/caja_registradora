# Generated by Django 4.2.3 on 2023-10-17 04:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_producto_foto'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroCajaDiaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion', models.CharField(max_length=255)),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]