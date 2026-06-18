from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db.models.signals import pre_delete,post_migrate
from django.db.utils import IntegrityError
from math import ceil
# models.py

import logging

logger = logging.getLogger(__name__)

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    roles = models.ManyToManyField(Rol, related_name='permisos', blank=True)

    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'


class Usuario(AbstractUser):
    PERMISOS_CHOICES = (
        ('cajero', 'Cajero'),
        ('admin', 'Administrador'),
        ('bodeguero', 'Bodeguero'),
    )
    VENTAS_CHOICES = (
        ('pruebas', 'Ventas de Pruebas'),
        ('normales', 'Sistema de Ventas Normales (Se registran)'),
    )
    
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    ventas_config = models.CharField(max_length=40, choices=VENTAS_CHOICES, default='normales')
    permisos = models.CharField(max_length=40, choices=PERMISOS_CHOICES, default='cajero')
    
    rut = models.CharField(max_length=40, null=True, verbose_name="Rut", default="", blank=True)
    clave_anulacion = models.CharField(max_length=128, default="", blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    def set_clave_anulacion(self, raw_clave):
        from django.contrib.auth.hashers import make_password
        self.clave_anulacion = make_password(raw_clave)
        self.save(update_fields=['clave_anulacion'])

    def check_clave_anulacion(self, raw_clave):
        from django.contrib.auth.hashers import check_password
        if self.clave_anulacion and self.clave_anulacion.startswith('pbkdf2_'):
            return check_password(raw_clave, self.clave_anulacion)
        return self.clave_anulacion == raw_clave


PERMISOS_PREDEFINIDOS = [
    ('acceso_caja', 'Acceso a caja', 'Usar la caja registradora', ['admin', 'cajero']),
    ('ver_productos', 'Ver productos', 'Ver lista de productos', ['admin', 'cajero', 'bodeguero']),
    ('editar_productos', 'Editar productos', 'Crear, editar y eliminar productos', ['admin', 'bodeguero']),
    ('importar_productos', 'Importar/exportar', 'Importar y exportar productos', ['admin', 'bodeguero']),
    ('ver_ventas', 'Ver ventas', 'Ver historial de ventas', ['admin', 'cajero']),
    ('anular_ventas', 'Anular ventas', 'Anular ventas realizadas', ['admin']),
    ('ver_reportes', 'Ver reportes', 'Ver reportes y calendario de cierres', ['admin', 'cajero']),
    ('ver_cuadre', 'Ver cuadre', 'Hacer cuadre de caja', ['admin', 'cajero']),
    ('ver_gastos', 'Ver gastos', 'Ver y registrar gastos', ['admin', 'cajero']),
    ('ver_configuracion', 'Ver configuración', 'Ver y editar configuración del sistema', ['admin']),
    ('gestionar_usuarios', 'Gestionar usuarios', 'Crear, editar y eliminar usuarios', ['admin']),
    ('gestionar_monedas', 'Gestionar monedas', 'Administrar monedas y tasas de cambio', ['admin']),
    ('gestionar_metodos_pago', 'Gestionar métodos de pago', 'Administrar métodos de pago', ['admin']),
    ('ver_logs', 'Ver logs', 'Ver logs del sistema', ['admin']),
    ('ver_actualizaciones', 'Ver actualizaciones', 'Verificar actualizaciones', ['admin']),
]


def crear_roles_permisos(**kwargs):
    roles_data = {
        'admin': 'Administrador completo del sistema',
        'cajero': 'Operador de caja registradora',
        'bodeguero': 'Encargado de bodega y productos',
    }
    for nombre, desc in roles_data.items():
        Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})

    for codigo, nombre, desc, roles_nombres in PERMISOS_PREDEFINIDOS:
        permiso, _ = Permiso.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre, 'descripcion': desc}
        )
        for rol_nombre in roles_nombres:
            rol = Rol.objects.filter(nombre=rol_nombre).first()
            if rol:
                permiso.roles.add(rol)

    rol_admin = Rol.objects.filter(nombre='admin').first()
    if rol_admin:
        Usuario.objects.filter(rol__isnull=True, permisos='admin').update(rol=rol_admin)
        Usuario.objects.filter(rol__isnull=True, permisos='cajero').update(rol=rol_admin)
        Usuario.objects.filter(rol__isnull=True, permisos='bodeguero').update(rol=rol_admin)

    print("Roles y permisos creados exitosamente.")


def crear_usuario_admin(**kwargs):
    if not Usuario.objects.filter(username='admin').exists():
        rol_admin = Rol.objects.filter(nombre='admin').first()
        Usuario.objects.create_superuser(
            username='admin', password='123',
            clave_anulacion='123', permisos='admin',
            rol=rol_admin,
        )
        print("Usuario administrador creado exitosamente.")
    else:
        admin = Usuario.objects.filter(username='admin').first()
        if admin and not admin.rol:
            rol_admin = Rol.objects.filter(nombre='admin').first()
            if rol_admin:
                admin.rol = rol_admin
                admin.save(update_fields=['rol'])


@receiver(post_migrate)
def post_migrate_callback(sender, **kwargs):
    if sender.name != 'core':
        return
    crear_roles_permisos(**kwargs)
    crear_usuario_admin(**kwargs)

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
    valor_costo = models.DecimalField(max_digits=12, decimal_places=2, default=0 )
    precio = models.DecimalField(max_digits=12, decimal_places=2)
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
        ('valor', 'Articulo por valor')
    )
    
    tipo_venta = models.CharField(max_length=10, choices=TIPO_VENTA_CHOICES, blank=False, null=False,default="unidad")
    

    def __str__(self):
        return self.nombre

class ProductoRapido(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tecla = models.CharField(max_length=2, blank=True, null=True, verbose_name="Atajo teclado")
    color = models.CharField(max_length=20, default='#6366f1', verbose_name="Color de botón")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        tecla = f" [{self.tecla}]" if self.tecla else ""
        return f"{self.producto.nombre}{tecla}"


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
    carrito_numero = models.PositiveIntegerField(default=1)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    gramaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    valor =  models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
        
    def subtotal(self):
        if self.producto.tipo_venta == 'gramaje':
            peso_en_gramos = self.gramaje or 0
            if self.producto.tipo_gramaje == 'kg':
                subtotal = peso_en_gramos * (self.producto.precio / 1000)
            else:
                subtotal = peso_en_gramos * self.producto.precio
        elif self.producto.tipo_venta == 'valor':
            subtotal = (self.valor or 0) * self.cantidad
        else:
            subtotal = self.cantidad * self.producto.precio

        # Redondea el subtotal al próximo múltiplo de 10 y asegura que no sea menor que 10.
        subtotal = max(10, ceil(subtotal / 10) * 10)

        return subtotal
    
class Moneda(models.Model):
    codigo = models.CharField(max_length=3, unique=True, verbose_name='Código (CLP, USD)')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    simbolo = models.CharField(max_length=5, default='$', verbose_name='Símbolo')
    decimales = models.PositiveSmallIntegerField(default=0, verbose_name='Decimales')
    separador_miles = models.CharField(max_length=1, default='.', verbose_name='Separador miles')
    separador_decimal = models.CharField(max_length=1, default=',', verbose_name='Separador decimal')
    locale = models.CharField(max_length=20, default='es-CL', verbose_name='Locale (es-CL, en-US)')
    activa = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
        ordering = ['orden']

    def __str__(self):
        return f'{self.codigo} ({self.simbolo})'


class TasaCambio(models.Model):
    moneda_origen = models.ForeignKey(Moneda, on_delete=models.CASCADE, related_name='tasas_origen')
    moneda_destino = models.ForeignKey(Moneda, on_delete=models.CASCADE, related_name='tasas_destino')
    tasa = models.DecimalField(max_digits=12, decimal_places=6, verbose_name='Tasa de cambio')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tasa de cambio'
        verbose_name_plural = 'Tasas de cambio'
        unique_together = ('moneda_origen', 'moneda_destino')

    def __str__(self):
        return f'1 {self.moneda_origen.codigo} = {self.tasa} {self.moneda_destino.codigo}'


class DenominacionMoneda(models.Model):
    TIPO_CHOICES = (('moneda', 'Moneda'), ('billete', 'Billete'))
    moneda = models.ForeignKey(Moneda, on_delete=models.CASCADE, related_name='denominaciones')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='billete')
    nombre = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Denominación'
        verbose_name_plural = 'Denominaciones'
        ordering = ['moneda', '-valor']

    def save(self, *args, **kwargs):
        if not self.nombre:
            self.nombre = f'{self.tipo.capitalize()} de ${int(self.valor):,}'.replace(',', '.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} ({self.moneda.codigo})'


class MetodoPago(models.Model):
    codigo = models.CharField(max_length=30, unique=True, verbose_name='Código interno')
    nombre = models.CharField(max_length=50, verbose_name='Nombre visible')
    icono = models.CharField(max_length=30, default='Money', verbose_name='Icono MUI')
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    requiere_autorizacion = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#6366f1', verbose_name='Color hex')
    abre_gaveta = models.BooleanField(default=False, verbose_name='Abre la gaveta')
    pide_monto = models.BooleanField(default=True, verbose_name='Pide monto al usuario')
    es_efectivo = models.BooleanField(default=False, verbose_name='Es efectivo (da vuelto)')
    da_vuelto = models.BooleanField(default=False, verbose_name='Puede dar vuelto')
    acepta_diferencia = models.BooleanField(default=True, verbose_name='Acepta pago de diferencia (resto)')

    class Meta:
        verbose_name = 'Método de pago'
        verbose_name_plural = 'Métodos de pago'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Configuracion(models.Model):
    id = models.AutoField(primary_key=True)
    decimales = models.PositiveIntegerField(default=2)
    clave_anulacion = models.CharField(max_length=20, blank=True, default='')
    idioma = models.CharField(max_length=20, blank=True, default='')
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
    separador_opciones = (
        ('1', 'Separar números por un < . > '),
        ('2', 'Separar números por un < , >'),
    )
    imprimir = models.CharField(max_length=20, choices=imprimir_opciones, default='no')
    separador= models.CharField(max_length=20, choices=separador_opciones, default='1')
    tipo_venta = models.CharField(max_length=20, choices=tipo_de_venta, default='1')
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    tamano_letra = models.PositiveIntegerField(default=10)

    TIPO_IMPRESORA_CHOICES = (
        ('usb', 'USB'),
        ('ip', 'IP'),
    )
    tipo_impresora = models.CharField(max_length=10, choices=TIPO_IMPRESORA_CHOICES, default='usb')
    ip_impresora = models.CharField(max_length=50, default='192.168.100.30', blank=True, null=True)
    puerto_impresora = models.PositiveIntegerField(default=9100, blank=True, null=True)

    TIPO_AUTORIZACION_CHOICES = (
        ('cualquier', 'Cualquier usuario con clave'),
        ('propio', 'Solo la clave del usuario actual'),
    )
    tipo_autorizacion = models.CharField(max_length=20, choices=TIPO_AUTORIZACION_CHOICES, default='cualquier')

    moneda_principal = models.ForeignKey(Moneda, on_delete=models.SET_NULL, null=True, blank=True, related_name='configs')
    redondeo_multiplo = models.PositiveIntegerField(default=10, verbose_name='Múltiplo de redondeo')
    debug_mode = models.BooleanField(default=False, verbose_name='Modo Debug')

    def __str__(self):
        return 'Configuración de la Aplicación'

@receiver(post_migrate)
def crear_configuracion(sender, **kwargs):
    if sender.name != 'core':
        return
    moneda_clp, _ = Moneda.objects.get_or_create(codigo='CLP', defaults={
        'nombre': 'Peso Chileno', 'simbolo': '$', 'decimales': 0,
        'separador_miles': '.', 'separador_decimal': ',', 'locale': 'es-CL',
        'activa': True, 'orden': 1,
    })
    Moneda.objects.get_or_create(codigo='USD', defaults={
        'nombre': 'Dólar Americano', 'simbolo': 'US$', 'decimales': 2,
        'separador_miles': ',', 'separador_decimal': '.', 'locale': 'en-US',
        'activa': True, 'orden': 2,
    })
    Moneda.objects.get_or_create(codigo='EUR', defaults={
        'nombre': 'Euro', 'simbolo': '€', 'decimales': 2,
        'separador_miles': '.', 'separador_decimal': ',', 'locale': 'de-DE',
        'activa': False, 'orden': 3,
    })
    Moneda.objects.get_or_create(codigo='ARS', defaults={
        'nombre': 'Peso Argentino', 'simbolo': '$', 'decimales': 2,
        'separador_miles': '.', 'separador_decimal': ',', 'locale': 'es-AR',
        'activa': False, 'orden': 4,
    })

    configuracion, created = Configuracion.objects.get_or_create(
        id=1,
        defaults={
            'decimales': 0,
            'clave_anulacion': '5901234123457',
            'idioma': 'es',
            'imprimir': 'sin_corte',
            'porcentaje_iva': 0.0,
            'tipo_venta': '1',
            'tamano_letra': 30,
            'separador': '1',
            'tipo_impresora': 'usb',
            'ip_impresora': '192.168.100.30',
            'puerto_impresora': 9100,
            'tipo_autorizacion': 'cualquier',
            'moneda_principal': moneda_clp,
            'redondeo_multiplo': 10,
            'debug_mode': False,
        }
    )
    if not configuracion.moneda_principal:
        configuracion.moneda_principal = moneda_clp
        configuracion.save(update_fields=['moneda_principal'])

    for valor, tipo, orden in [
        (10, 'moneda', 1), (50, 'moneda', 2), (100, 'moneda', 3), (500, 'moneda', 4),
        (1000, 'billete', 5), (2000, 'billete', 6), (5000, 'billete', 7),
        (10000, 'billete', 8), (20000, 'billete', 9),
    ]:
        DenominacionMoneda.objects.get_or_create(
            moneda=moneda_clp, valor=valor,
            defaults={'tipo': tipo, 'orden': orden}
        )

    for codigo, nombre, icono, color, orden, props in [
        ('efectivo', 'Efectivo', 'Money', '#22c55e', 1, {'abre_gaveta': True, 'pide_monto': True, 'es_efectivo': True, 'da_vuelto': True, 'acepta_diferencia': False}),
        ('efectivo_justo', 'Efectivo Justo', 'Money', '#16a34a', 2, {'abre_gaveta': True, 'pide_monto': True, 'es_efectivo': True, 'da_vuelto': False, 'acepta_diferencia': False}),
        ('debito', 'Débito', 'CreditCard', '#6366f1', 3, {'abre_gaveta': False, 'pide_monto': False, 'es_efectivo': False, 'da_vuelto': False, 'acepta_diferencia': True}),
        ('credito', 'Crédito', 'CreditCard', '#8b5cf6', 4, {'abre_gaveta': False, 'pide_monto': False, 'es_efectivo': False, 'da_vuelto': False, 'acepta_diferencia': True}),
        ('transferencia', 'Transferencia', 'SwapHoriz', '#f59e0b', 5, {'abre_gaveta': False, 'pide_monto': False, 'es_efectivo': False, 'da_vuelto': False, 'acepta_diferencia': True}),
    ]:
        MetodoPago.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre, 'icono': icono, 'color': color, 'orden': orden, **props}
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


@receiver(post_migrate)
def crear_caja_iaria(sender, **kwargs):
    caja_diaria = [
    {
        'monto': 0.0,
        'retiro' : 0.0,
    },
    ]
    if CajaDiaria.objects.count() == 0:
        print(" Ingresando datos iniciales ...")
        for caja in caja_diaria:
            CajaDiaria.objects.get_or_create(**caja)

        print(" Datos iniciales creados correctamente")


class Cuadre(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Cierre de caja por {self.usuario.username} el {self.fecha_ingreso}'
    

class RetiroCaja(models.Model):
    MONTO_OPCIONES = (
        ('restado', 'Restado'),
        ('sumado', 'Sumado'),
    )
    
    monto = models.DecimalField(max_digits=10,decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Referencia al usuario que hizo el retiro
    fecha_hora = models.DateTimeField(auto_now_add=True)  # Guarda la fecha y hora del retiro
    tipo_monto = models.CharField(choices=MONTO_OPCIONES)  # Si el monto fue restado o sumado

    def __str__(self): 
        return f'Retiro de ${self.monto} - {self.tipo_monto} - Realizado por: {self.usuario.username} el {self.fecha_hora}'

class ActualizacionModel(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_actualizacion = models.DateTimeField()
    version = models.CharField(max_length=150)



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
    
class RegistroCajaDiaria(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, default=1)# Asigna un valor predeterminado (por ejemplo, 1)

    def __str__(self):
        return f'Gasto de ${self.monto} - {self.descripcion} - {self.fecha_hora}'

@receiver(post_migrate)
def crear_fecha_inicial(sender, **kwargs):
    # Verificar si ya existe una instancia de ActualizacionModel
    if not ActualizacionModel.objects.exists():
        # Crear una instancia con la fecha inicial
        fecha_inicial = timezone.now()
        ActualizacionModel.objects.create(fecha_actualizacion=fecha_inicial)


@receiver(pre_delete, sender=Producto)
def log_producto_deletion(sender, instance, **kwargs):
    # Obtiene el usuario que realizó la eliminación del producto (si está disponible)
    user = None
    if hasattr(instance, 'user'):
        user = instance.user.username

    logger.info(f"Producto eliminado: {instance.nombre} (ID: {instance.id_producto}), Eliminado por: {user}")
