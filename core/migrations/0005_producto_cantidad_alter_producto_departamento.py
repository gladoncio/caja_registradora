# Generated by Django 4.2.3 on 2023-08-19 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_producto_id_alter_producto_codigo_barras_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='cantidad',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productos_cantidad', to='core.departamento'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='departamento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productos_departamento', to='core.departamento'),
        ),
    ]