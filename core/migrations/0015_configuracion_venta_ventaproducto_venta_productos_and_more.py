# Generated by Django 4.2.3 on 2023-08-25 04:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_carritoitem_gramaje_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decimales', models.PositiveIntegerField(default=2)),
                ('clave_anulacion', models.CharField(max_length=20)),
                ('idioma', models.CharField(max_length=20)),
                ('imprimir', models.CharField(choices=[('no', 'No imprimir'), ('con_corte', 'Imprimir con corte'), ('sin_corte', 'Imprimir sin corte')], default='no', max_length=20)),
                ('porcentaje_iva', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('valor_iva', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='VentaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('gramaje', models.DecimalField(decimal_places=2, max_digits=6)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.producto')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.venta')),
            ],
        ),
        migrations.AddField(
            model_name='venta',
            name='productos',
            field=models.ManyToManyField(through='core.VentaProducto', to='core.producto'),
        ),
        migrations.AddField(
            model_name='venta',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]