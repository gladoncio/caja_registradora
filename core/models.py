from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models.signals import pre_delete



class Usuario(AbstractUser):
    # Define las opciones de permisos como una tupla de tuplas
    PERMISOS_CHOICES = (
        ('cajero', 'Cajero'),
        ('admin', 'Administrador'),
        ('bodeguero', 'Bodeguero'),
        # Agrega otras opciones según tus necesidades
    )
    
    permisos = models.CharField(
        max_length=40,
        null=True,
        verbose_name="Permiso",
        default="Cajero",
        choices=PERMISOS_CHOICES,  # Asigna las opciones como choices
    )
    
    rut = models.CharField(max_length=40, null=True, verbose_name="Rut", default="", blank=True)

    # Resto de los campos y métodos de tu modelo

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
    descripcion = models.TextField(blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='productos_departamento', blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    TIPO_GRAMAJE_CHOICES = (
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('Ml', 'Mililitros'),
        ('L', 'Litros'),
    )
    tipo_gramaje = models.CharField(max_length=2, choices=TIPO_GRAMAJE_CHOICES, blank=True, null=True)

    TIPO_VENTA_CHOICES = (
        ('unidad', 'Artículo por unidad'),
        ('gramaje', 'Artículo por gramaje'),
    )
    tipo_venta = models.CharField(max_length=10, choices=TIPO_VENTA_CHOICES, blank=False, null=False,default="unidad")
    

    def __str__(self):
        return self.nombre


class Stock(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, primary_key=True)
    cantidad = models.PositiveIntegerField(default=0)
    gramaje = models.PositiveIntegerField(default=0)
    TIPO_GRAMAJE_CHOICES = (
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
    )
    tipo_gramaje = models.CharField(max_length=2, choices=TIPO_GRAMAJE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"Cantidad de {self.producto.nombre}: {self.cantidad}"



class CarritoItem(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    gramaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
        
    def subtotal(self):
        if self.producto.tipo_venta == 'gramaje':
            peso_en_gramos = self.gramaje
            if self.producto.tipo_gramaje == 'kg':
                return peso_en_gramos * (self.producto.precio / 1000)
            else:
                return peso_en_gramos * self.producto.precio
        else:
            return self.cantidad * self.producto.precio
        
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} para {self.usuario.username}"
    
class Configuracion(models.Model):
    id = models.AutoField(primary_key=True)
    decimales = models.PositiveIntegerField(default=2)
    clave_anulacion = models.CharField(max_length=20)
    idioma = models.CharField(max_length=20)
    imprimir_opciones = (
        ('no', 'No imprimir'),
        ('con_corte', 'Imprimir con corte'),
        ('sin_corte', 'Imprimir sin corte'),
    )
    imprimir = models.CharField(max_length=20, choices=imprimir_opciones, default='no')
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Agrega el campo para el tamaño de letra
    tamano_letra = models.PositiveIntegerField(default=10)  # Ejemplo: tamaño de letra por defecto de 10 puntos

    def __str__(self):
        return 'Configuración de la Aplicación'




class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField(default=timezone.now)
    productos = models.ManyToManyField(Producto, through='VentaProducto')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # Otros campos según tus necesidades

    def __str__(self):
        return f'Venta #{self.id} - {self.fecha_hora}'


class VentaProducto(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(blank=True, null=True)
    gramaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # Otros campos relacionados con la venta de cada producto

    def __str__(self):
        return f'{self.producto} en Venta #{self.venta.id}'

class FormaPago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    # Agregar campo para el tipo de pago
    TIPO_PAGO_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
    )
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.tipo_pago} - Monto: {self.monto}'
    

class RegistroTransaccion(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)

    # Detalles de los montos por tipo de pago
    monto_efectivo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_credito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_debito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_transferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_retiro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    

    # Campo para el valor de la caja diaria
    valor_caja_diaria = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'Registro #{self.id} - Fecha: {self.fecha_ingreso} - Monto Total: {self.monto_total}'
    
class CajaDiaria(models.Model):
    id = models.AutoField(primary_key=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    retiro = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f'Caja Diaria #{self.id} - Monto: {self.monto}'
    
class Cuadre(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Cierre de caja por {self.usuario.username} el {self.fecha_ingreso}'
    


class ActualizacionModel(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_actualizacion = models.DateTimeField()

class VentaEliminada(models.Model):
    fecha_hora_eliminacion = models.DateTimeField(default=timezone.now)
    productos_eliminados = models.TextField() 
    total_eliminado = models.DecimalField(max_digits=10, decimal_places=2)
    usuario_eliminador = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Venta Eliminada - Fecha: {self.fecha_hora_eliminacion}'

# Definición de funciones y señales para el manejo de la eliminación de ventas
@receiver(pre_delete, sender=Venta)
def venta_eliminar_handler(sender, instance, **kwargs):
    productos_eliminados = instance.productos.all()
    total_eliminado = instance.total
    usuario_eliminador = instance.usuario
    
    venta_eliminada = VentaEliminada(
        fecha_hora_eliminacion=timezone.now(),
        productos_eliminados=productos_eliminados, 
        total_eliminado=total_eliminado,
        usuario_eliminador=usuario_eliminador,
        # Agrega otros campos según tus necesidades
    )
    venta_eliminada.save()