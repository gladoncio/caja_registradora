# Generated by Django 4.2.3 on 2023-10-17 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_venta_vuelto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='foto',
            field=models.ImageField(blank=True, default='productos/default.jpg', null=True, upload_to='productos/'),
        ),
    ]