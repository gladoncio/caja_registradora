# Generated by Django 4.2.3 on 2023-09-08 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_actualizacionmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualizacionmodel',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]