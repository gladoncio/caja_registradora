"""
Script para generar datos de prueba masivos.
Ejecutar: python app/manage.py runserver (esperar a que termine)
O: docker exec caja_registradora-caja-1 python app/manage.py shell < app/core/seed_data.py
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cash_register.settings')
sys.path.insert(0, '/app/app')
django.setup()

from core.models import *

print('🧹 Limpiando datos existentes...')
CarritoItem.objects.all().delete()
VentaProducto.objects.all().delete()
FormaPago.objects.all().delete()
Venta.objects.all().delete()
Producto.objects.all().delete()
ProductoRapido.objects.all().delete()
Departamento.objects.all().delete()
Marca.objects.all().delete()
GastoCaja.objects.all().delete()
RegistroTransaccion.objects.all().delete()

print('🏷️ Creando departamentos...')
deptos = ['Abarrotes', 'Lácteos', 'Bebidas', 'Limpieza', 'Panadería', 'Carnicería', 'Verdulería', 'Farmacia', 'Librería', 'Mascotas']
deptos_objs = []
for d in deptos:
    deptos_objs.append(Departamento.objects.create(nombre=d))

print('🏷️ Creando marcas...')
marcas = ['Coca-Cola', 'Nestlé', 'Watt\'s', 'Lucchetti', 'Carozzi', 'Tresmontes', 'Ideal', 'Soprole', 'Colún', 'Líder']
marcas_objs = []
for m in marcas:
    marcas_objs.append(Marca.objects.create(nombre=m))

print('📦 Creando 500 productos...')
nombres_base = [
    'Arroz', 'Fideos', 'Aceite', 'Harina', 'Azúcar', 'Sal', 'Café', 'Té', 'Leche', 'Yogurt',
    'Queso', 'Mantequilla', 'Pan', 'Jabón', 'Detergente', 'Shampoo', 'Desodorante', 'Papel higiénico',
    'Agua mineral', 'Jugo', 'Cerveza', 'Vino', 'Galletas', 'Chocolate', 'Carne molida', 'Pollo',
    'Manzana', 'Plátano', 'Naranja', 'Tomate', 'Cebolla', 'Papas', 'Atún', 'Sardinas', 'Mayonesa',
    'Ketchup', 'Mostaza', 'Vinagre', 'Salsa de tomate', 'Mermelada', 'Dulce de leche', 'Leche condensada',
    'Crema', 'Mantequilla', 'Margarina', 'Huevos', 'Lechuga', 'Zanahoria', 'Brócoli', 'Coliflor',
]
precios_base = [500, 800, 1200, 1800, 2500, 3500, 4500, 6000, 8000, 10000, 15000, 20000, 30000]

productos_creados = 0
for i in range(500):
    nombre = f"{random.choice(nombres_base)} {random.choice(['Premium', 'Clásico', 'Económico', 'Familiar', 'Individual', 'Plus', 'Ultra', 'Mega', '', 'Deluxe'])} {random.randint(1, 999)}g"
    # Evitar duplicados aproximados
    if Producto.objects.filter(nombre=nombre).exists():
        continue
    precio_base = random.choice(precios_base) + random.randint(-200, 200)
    costo = int(precio_base * random.uniform(0.4, 0.75))
    barcode = f'780{random.randint(100000000, 999999999)}'
    Producto.objects.create(
        nombre=nombre,
        precio=precio_base,
        valor_costo=costo,
        codigo_barras=barcode,
        departamento=random.choice(deptos_objs),
        marca=random.choice(marcas_objs),
        tipo_venta=random.choice(['unidad', 'unidad', 'unidad', 'gramaje']),
        descripcion=f'Producto de prueba: {nombre}',
    )
    productos_creados += 1

print(f'✅ {productos_creados} productos creados')

print('⭐ Creando productos rápidos...')
for p in Producto.objects.order_by('?')[:12]:
    ProductoRapido.objects.get_or_create(producto=p)

print('💰 Creando ventas de prueba...')
if not Usuario.objects.filter(username='admin').exists():
    admin = Usuario.objects.create_superuser(username='admin', password='123', clave_anulacion='123', permisos='admin')
else:
    admin = Usuario.objects.get(username='admin')

# Crear algunas ventas en los últimos 30 días
for dia in range(30):
    fecha = datetime.now() - timedelta(days=dia)
    for _ in range(random.randint(3, 15)):
        total = 0
        venta = Venta.objects.create(
            fecha_hora=fecha + timedelta(hours=random.randint(8, 22), minutes=random.randint(0, 59)),
            total=0,
            vuelto=0,
            usuario=admin,
        )
        productos = Producto.objects.order_by('?')[:random.randint(1, 8)]
        for p in productos:
            cant = random.randint(1, 5)
            subtotal = p.precio * cant
            VentaProducto.objects.create(
                venta=venta, producto=p,
                cantidad=cant, subtotal=subtotal,
            )
            total += subtotal

        tipo_pago = random.choice(['efectivo', 'efectivo', 'debito', 'transferencia'])
        FormaPago.objects.create(venta=venta, tipo_pago=tipo_pago, monto=total)
        venta.total = total
        venta.vuelto = random.randint(0, 5000) if tipo_pago == 'efectivo' else 0
        venta.save()

print('✅ Ventas de prueba creadas')

# Crear algunos gastos
print('📋 Creando gastos...')
desc_gastos = ['Pago luz', 'Pago agua', 'Arriendo', 'Reposición', 'Flete', 'Aseo', 'Otros']
for _ in range(20):
    GastoCaja.objects.create(
        monto=random.randint(5000, 50000),
        descripcion=random.choice(desc_gastos),
        usuario=admin,
        fecha_hora=datetime.now() - timedelta(days=random.randint(0, 15), hours=random.randint(8, 18)),
    )

print('📊 Creando cierres...')
for dia in range(5, 30, 5):
    ventas = Venta.objects.filter(fecha_hora__gte=datetime.now() - timedelta(days=dia + 5), fecha_hora__lte=datetime.now() - timedelta(days=dia))
    monto_efectivo = FormaPago.objects.filter(venta__in=ventas, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_debito = FormaPago.objects.filter(venta__in=ventas, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_transferencia = FormaPago.objects.filter(venta__in=ventas, tipo_pago='transferencia').aggregate(Sum('monto'))['monto__sum'] or 0
    RegistroTransaccion.objects.create(
        fecha_ingreso=datetime.now() - timedelta(days=dia, hours=22),
        monto_total=ventas.aggregate(Sum('total'))['total__sum'] or 0,
        monto_efectivo=monto_efectivo,
        monto_debito=monto_debito,
        monto_transferencia=monto_transferencia,
    )

print(f'✅ Total: {Producto.objects.count()} productos, {Venta.objects.count()} ventas, {RegistroTransaccion.objects.count()} cierres')
print('🎉 Listo!')
