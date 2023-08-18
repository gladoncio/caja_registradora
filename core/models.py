from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    permisos = models.CharField(max_length=40, null=True, verbose_name="Permiso", default="1")
    rut = models.CharField(max_length=40, null=True, verbose_name="Rut", default="")

class Departamento(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_barras = models.CharField(max_length=20, unique=True, blank=True, null=True)
    gramaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    foto = models.ImageField(upload_to='productos/', null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)  # Campo para la descripción
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)  # Relación con Marca

    def __str__(self):
        return self.nombre

class Stock(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, primary_key=True)  # Relación uno a uno con Producto
    cantidad = models.PositiveIntegerField(default=0)  # Campo para la cantidad en stock

    def __str__(self):
        return f"Cantidad de {self.producto.nombre}: {self.cantidad}"
