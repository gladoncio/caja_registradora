# Generated by Django 4.2.3 on 2023-08-25 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_configuracion_venta_ventaproducto_venta_productos_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]