from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import *
from .models import *
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import F
from decimal import Decimal

# Create your views here.

def login(request):
    return render(request, 'login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect(index)


@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')

def caja(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in carrito_items)
    return render(request, 'caja.html', {'carrito_items': carrito_items, 'total': total})


@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    if request.method == 'POST':
        opcion = request.POST.get('opcion')
        if opcion == 'gramaje':
            peso = float(request.POST.get('peso'))
            tipo_gramaje = request.POST.get('tipo_gramaje')
            if tipo_gramaje == 'kg':
                print("kg")
                peso_en_gramos = peso * 1000
                print (peso_en_gramos)
            else:
                print("gr")
                peso_en_gramos = peso
                print (peso_en_gramos)
            carrito_item, created = CarritoItem.objects.get_or_create(usuario=request.user, producto=producto)
            if not created:
                carrito_item.gramaje = F('gramaje') + peso_en_gramos
                carrito_item.cantidad = 0  # Reiniciamos la cantidad si se agrega por peso
                carrito_item.save()
            else:
                carrito_item.gramaje = peso_en_gramos
                carrito_item.cantidad = 0  # Reiniciamos la cantidad si se agrega por peso
                carrito_item.save()
            # Restar el stock si es necesario
        else:
            cantidad = int(request.POST.get('cantidad', 1))
            carrito_item, created = CarritoItem.objects.get_or_create(usuario=request.user, producto=producto)
            if not created:
                carrito_item.cantidad = F('cantidad') + cantidad
                carrito_item.gramaje = None  # Reiniciamos el gramaje si se agrega por cantidad
                carrito_item.save()
            else:
                carrito_item.cantidad = cantidad
                carrito_item.gramaje = None  # Reiniciamos el gramaje si se agrega por cantidad
                carrito_item.save()
            # Restar el stock si es necesario
    
    return redirect('caja')


@login_required
def eliminar_item(request, item_id):
    try:
        if request.method == 'POST':
            config = Configuracion.objects.get(id=1)
            clave_ingresada = request.POST.get('clave_anulacion')
            if clave_ingresada == config.clave_anulacion:
                print(config.clave_anulacion)
                producto = Producto.objects.get(id_producto=item_id)
                item = CarritoItem.objects.get(producto=producto, usuario=request.user)
                item.delete()
                print("Eliminado con éxito")
            else:
                print("clave invalida")
    except CarritoItem.DoesNotExist:
        print("El ítem no existe")

    return redirect('caja')


@login_required
def generar_venta(request,parametro1,parametro2,parametro3):
    print(parametro1)
    print(parametro2)
    print(parametro3)
    try:
        carrito_items = CarritoItem.objects.filter(usuario=request.user)
        
        if carrito_items.exists():
            # Crear una nueva venta
            nueva_venta = Venta(usuario=request.user, total=0)
            nueva_venta.save()
            
            
            # Variable para almacenar el total de la venta
            total_venta = Decimal('0.00')
            # Agregar productos al modelo VentaProducto
            for item in carrito_items:
                subtotal = item.subtotal()
                total_venta += subtotal
                VentaProducto.objects.create(venta=nueva_venta,producto=item.producto,cantidad=item.cantidad,gramaje=item.gramaje,subtotal=subtotal)
            nueva_venta.total = total_venta
            nueva_venta.save()
            
            # Vaciar el carrito del usuario
            carrito_items.delete()
            
            # Redireccionar a la página de éxito o factura
            return redirect('caja')  # Cambiar por la página deseada
        else:
            # Manejar el caso donde el carrito del usuario está vacío
            pass
    except Exception as e:
        # Manejar excepciones u otros errores
        pass
    
    # Redireccionar a la página del carrito si ocurre algún error
    return redirect('caja')  # Cambiar por la página del carrito
