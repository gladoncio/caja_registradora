from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models.signals import pre_delete,post_migrate
from django.db.utils import IntegrityError



class Usuario(AbstractUser):
    # Define las opciones de permisos como una tupla de tuplas
    PERMISOS_CHOICES = (
        ('cajero', 'Cajero'),
        ('admin', 'Administrador'),
        ('bodeguero', 'Bodeguero'),
    )
    
    permisos = models.CharField(
        max_length=40,
        null=True,
        verbose_name="Permiso",
        default="Cajero",
        choices=PERMISOS_CHOICES,  # Asigna las opciones como choices
    )
    
    rut = models.CharField(max_length=40, null=True, verbose_name="Rut", default="", blank=True)
    clave_anulacion = models.CharField(max_length=20, default="", unique=True)  # Hacer la clave única



# Define la función para crear el usuario admin
def crear_usuario_admin(**kwargs):
    if not Usuario.objects.filter(username='admin').exists():
        Usuario.objects.create_superuser(username='admin', password='123', clave_anulacion='123', permisos='admin')
        print("Usuario administrador creado exitosamente.")

# Registra la función con la señal post_migrate
@receiver(post_migrate)
def post_migrate_callback(sender, **kwargs):
    crear_usuario_admin(**kwargs)

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
    foto = models.ImageField(upload_to='productos/', null=True, blank=True, default='productos/default.jpg')
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
    tipo_de_venta = (
        ('1', 'No registrar Stock'),
        ('2', 'Registrar Stock con Descuento'),
        ('3', 'Registrar el stock de las ventas'),
    )
    imprimir = models.CharField(max_length=20, choices=imprimir_opciones, default='no')
    tipo_venta = models.CharField(max_length=20, choices=tipo_de_venta, default='1')
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Agrega el campo para el tamaño de letra
    tamano_letra = models.PositiveIntegerField(default=10)  # Ejemplo: tamaño de letra por defecto de 10 puntos

    def __str__(self):
        return 'Configuración de la Aplicación'

@receiver(post_migrate)
def crear_configuracion(sender, **kwargs):  # Reemplaza 'tu_app_nombre' con el nombre de tu aplicación
        configuracion, created = Configuracion.objects.get_or_create(
            decimales = 0,
            clave_anulacion = '5901234123457',
            idioma = 'es',
            imprimir = 'sin_corte',
            porcentaje_iva = 0.0,
            tipo_venta = '1',
            tamano_letra = 30,
        )


class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_hora = models.DateTimeField(default=timezone.now)
    productos = models.ManyToManyField(Producto, through='VentaProducto')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # Otros campos según tus necesidades

    def __str__(self):
        return f'Venta #{self.id} - {self.fecha_hora}'

    class Meta:
        verbose_name_plural = 'Ventas'

class VentaProducto(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
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


# Modelos de copia de seguridad
class VentaRespaldo(models.Model):
    venta_original_id = models.PositiveIntegerField(default=0)
    fecha_hora = models.DateTimeField()
    fecha_anulacion = models.DateTimeField(default=timezone.now)  # Establece un valor predeterminado
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)


class VentaProductoRespaldo(models.Model):
    venta = models.ForeignKey(VentaRespaldo, on_delete=models.CASCADE,default=None) # Campo para almacenar la ID de la venta original
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(blank=True, null=True)
    gramaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

class FormaPagoRespaldo(models.Model):
    venta = models.ForeignKey(VentaRespaldo, on_delete=models.CASCADE, default=None)  # Agrega default=None
    tipo_pago = models.CharField(max_length=20)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

@receiver(pre_delete, sender=Venta)
def crear_copia_venta(sender, instance, **kwargs):
    # Crear copia de seguridad de la venta original
    copia_venta = VentaRespaldo(
        venta_original_id=instance.id,  # Almacenar la ID de la venta original
        fecha_hora=instance.fecha_hora,
        total=instance.total,
        usuario=instance.usuario
    )
    copia_venta.save()

    # Crear copias de seguridad de los productos de venta originales
    for venta_producto in instance.ventaproducto_set.all():
        copia_producto = VentaProductoRespaldo(
            venta=copia_venta,  # Asignar la copia de venta como venta original en copia de producto
            producto=venta_producto.producto,
            cantidad=venta_producto.cantidad,
            gramaje=venta_producto.gramaje,
            subtotal=venta_producto.subtotal
        )
        copia_producto.save()

    # Crear copias de seguridad de las formas de pago
    for forma_pago in instance.formapago_set.all():
        copia_forma_pago = FormaPagoRespaldo(
            venta=copia_venta,  # Asignar la copia de venta como venta original en copia de forma de pago
            tipo_pago=forma_pago.tipo_pago,
            monto=forma_pago.monto
        )
        copia_forma_pago.save()

    # No es necesario eliminar la venta original aquí, ya que el sistema de señales se encarga de ello


class GastoCaja(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, default=1)# Asigna un valor predeterminado (por ejemplo, 1)

    def __str__(self):
        return f'Gasto de ${self.monto} - {self.descripcion} - {self.fecha_hora}'


