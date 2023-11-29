from multiprocessing import context
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import *
from .models import *
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import F,Q,Max
from decimal import Decimal
import datetime
from escpos.printer import Usb
from usb.core import USBError
from django.http import HttpResponse
import requests
import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from .funciones import check_github_version
import barcode
from barcode import generate
from django.conf import settings  # Agrega esta importación
from io import BytesIO
from django.urls import reverse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist  # Importa la excepción ObjectDoesNotExist
from barcode.writer import ImageWriter
import random
from barcode import EAN13
from django.core.paginator import Paginator
from django.views.generic import ListView
from math import ceil
from escpos import *
from .impresora import abrir_caja_impresora, imprimir, imprimir_en_xprinter, generar_y_imprimir_codigo_ean13, generar_comandos_de_impresion
import locale
from django.utils.formats import date_format
import json









# ██╗░░░░░░█████╗░░██████╗░██╗███╗░░██╗  ██╗░░░██╗██╗███████╗░██╗░░░░░░░██╗░██████╗
# ██║░░░░░██╔══██╗██╔════╝░██║████╗░██║  ██║░░░██║██║██╔════╝░██║░░██╗░░██║██╔════╝
# ██║░░░░░██║░░██║██║░░██╗░██║██╔██╗██║  ╚██╗░██╔╝██║█████╗░░░╚██╗████╗██╔╝╚█████╗░
# ██║░░░░░██║░░██║██║░░╚██╗██║██║╚████║  ░╚████╔╝░██║██╔══╝░░░░████╔═████║░░╚═══██╗
# ███████╗╚█████╔╝╚██████╔╝██║██║░╚███║  ░░╚██╔╝░░██║███████╗░░╚██╔╝░╚██╔╝░██████╔╝
# ╚══════╝░╚════╝░░╚═════╝░╚═╝╚═╝░░╚══╝  ░░░╚═╝░░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░╚═════╝░


def login(request):
    return render(request, 'login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect(index)



# ██████╗░██╗░░░██╗░██████╗░█████╗░░█████╗░██████╗░░█████╗░██████╗░  ██╗███╗░░██╗██████╗░███████╗██╗░░██╗
# ██╔══██╗██║░░░██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗  ██║████╗░██║██╔══██╗██╔════╝╚██╗██╔╝
# ██████╦╝██║░░░██║╚█████╗░██║░░╚═╝███████║██║░░██║██║░░██║██████╔╝  ██║██╔██╗██║██║░░██║█████╗░░░╚███╔╝░
# ██╔══██╗██║░░░██║░╚═══██╗██║░░██╗██╔══██║██║░░██║██║░░██║██╔══██╗  ██║██║╚████║██║░░██║██╔══╝░░░██╔██╗░
# ██████╦╝╚██████╔╝██████╔╝╚█████╔╝██║░░██║██████╔╝╚█████╔╝██║░░██║  ██║██║░╚███║██████╔╝███████╗██╔╝╚██╗
# ╚═════╝░░╚═════╝░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚═╝  ╚═╝╚═╝░░╚══╝╚═════╝░╚══════╝╚═╝░░╚═╝

@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')


# ░█████╗░░█████╗░░░░░░██╗░█████╗░
# ██╔══██╗██╔══██╗░░░░░██║██╔══██╗
# ██║░░╚═╝███████║░░░░░██║███████║
# ██║░░██╗██╔══██║██╗░░██║██╔══██║
# ╚█████╔╝██║░░██║╚█████╔╝██║░░██║
# ░╚════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝
@login_required(login_url='/login')
def caja(request):
    accion = "nada"
    id = 0
    config = Configuracion.objects.get(id=1)
    carrito_items = CarritoItem.objects.filter(usuario=request.user).order_by('-fecha_agregado')
    total = sum(item.subtotal() for item in carrito_items)
    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            try:
                producto = Producto.objects.get(codigo_barras=barcode)
                if producto.tipo_venta == 'unidad':
                    if config.tipo_venta == '2':
                        try:
                            stock = producto.stock
                        except ObjectDoesNotExist:
                        # Si el objeto Stock no existe, maneja la situación aquí
                            messages.success(request, 'El producto no tiene Stock.')
                            return redirect(caja)
                    # Busca si ya existe un carrito_item con el mismo producto y usuario
                    carrito_item, created = CarritoItem.objects.get_or_create(
                        usuario=request.user,
                        producto=producto,
                        defaults={'cantidad': 1}  # Cantidad predeterminada si no existe
                    )
                    if not created:
                        # Si el carrito_item ya existe, simplemente aumenta la cantidad en 1
                        carrito_item.cantidad += 1
                        carrito_item.save()
                    # Redirige a la misma vista
                    return redirect('caja')
                elif producto.tipo_venta == 'valor':
                    id_producto = producto.id_producto
                    accion = "variable"
                    form_valor = ValorForm(request.POST)
                    context = {'form': form,'carrito_items': carrito_items, 'total': total, 'accion' : accion, 'id_producto' : id_producto, 'form_valor' : form_valor}
                    return render(request, 'caja.html', context)
                    print("articulo por valor")
                else:
                    messages.success(request, 'El producto es por gramaje.')
            except Producto.DoesNotExist:
                productos_similares = Producto.objects.filter(nombre__icontains=barcode)
                if productos_similares.exists():
                    return render(request, 'caja.html', {'form': form, 'carrito_items': carrito_items, 'total': total, 'productos_similares': productos_similares, 'id_producto' : id})
                    pass
                else:
                    print("no confidencias ni existencias")
    else:
        form = BarcodeForm()

    total = round(total)
    total = total // 10 * 10
    context = {
        'form': form,
        'carrito_items': carrito_items,
        'total' : total,
        'id_producto' : id
        # Otros datos de contexto que necesites
    }
    return render(request, 'caja.html', context)

@login_required(login_url='/login')
def agregar_producto_al_carrito(request, id_producto):
    config = Configuracion.objects.get(id=1)
    carrito_items = CarritoItem.objects.filter(usuario=request.user).order_by('-fecha_agregado')
    if request.method == 'POST':
        form = ValorForm(request.POST)  # Crear una instancia del formulario con los datos POST
        if form.is_valid():
            valor = form.cleaned_data['valor']
            producto = Producto.objects.get(id_producto = id_producto)

            carrito_item, created = CarritoItem.objects.get_or_create(
                usuario=request.user,
                producto=producto,
                defaults={'cantidad': 1},
                valor = valor  # Cantidad predeterminada si no existe
            )
            if not created:
                carrito_item.valor = carrito_item.valor + valor
                carrito_item.cantidad += 1
                carrito_item.save()

            return redirect('caja')

    return redirect('caja')




# ░█████╗░░██████╗░██████╗░███████╗░██████╗░░█████╗░██████╗░  ░█████╗░██╗░░░░░
# ██╔══██╗██╔════╝░██╔══██╗██╔════╝██╔════╝░██╔══██╗██╔══██╗  ██╔══██╗██║░░░░░
# ███████║██║░░██╗░██████╔╝█████╗░░██║░░██╗░███████║██████╔╝  ███████║██║░░░░░
# ██╔══██║██║░░╚██╗██╔══██╗██╔══╝░░██║░░╚██╗██╔══██║██╔══██╗  ██╔══██║██║░░░░░
# ██║░░██║╚██████╔╝██║░░██║███████╗╚██████╔╝██║░░██║██║░░██║  ██║░░██║███████╗
# ╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝╚══════╝░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝  ╚═╝░░╚═╝╚══════╝

# ░█████╗░░█████╗░██████╗░██████╗░██╗████████╗░█████╗░
# ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
# ██║░░╚═╝███████║██████╔╝██████╔╝██║░░░██║░░░██║░░██║
# ██║░░██╗██╔══██║██╔══██╗██╔══██╗██║░░░██║░░░██║░░██║
# ╚█████╔╝██║░░██║██║░░██║██║░░██║██║░░░██║░░░╚█████╔╝
# ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░╚═╝░░░░╚════╝░

@login_required(login_url='/login')
def agregar_al_carrito(request, producto_id):
    config = Configuracion.objects.get(id=1)
    producto = get_object_or_404(Producto, id_producto=producto_id)
    if request.method == 'POST':
        opcion = request.POST.get('opcion')
        if opcion == 'gramaje':
            peso = float(request.POST.get('peso'))
            tipo_gramaje = request.POST.get('tipo_gramaje')
            if tipo_gramaje == 'kg':
                peso_en_gramos = peso * 1000
            else:
                peso_en_gramos = peso
            carrito_item, created = CarritoItem.objects.get_or_create(usuario=request.user, producto=producto)
            if not created:
                carrito_item.gramaje = F('gramaje') + peso_en_gramos
                carrito_item.cantidad = 0  # Reiniciamos la cantidad si se agrega por peso
                carrito_item.save()
            else:
                carrito_item.gramaje = peso_en_gramos
                carrito_item.cantidad = 0  # Reiniciamos la cantidad si se agrega por peso
                carrito_item.save()
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

        
    
    return redirect('caja')



# ███████╗██╗░░░░░██╗███╗░░░███╗██╗███╗░░██╗░█████╗░██████╗░  ██████╗░███████╗██╗░░░░░
# ██╔════╝██║░░░░░██║████╗░████║██║████╗░██║██╔══██╗██╔══██╗  ██╔══██╗██╔════╝██║░░░░░
# █████╗░░██║░░░░░██║██╔████╔██║██║██╔██╗██║███████║██████╔╝  ██║░░██║█████╗░░██║░░░░░
# ██╔══╝░░██║░░░░░██║██║╚██╔╝██║██║██║╚████║██╔══██║██╔══██╗  ██║░░██║██╔══╝░░██║░░░░░
# ███████╗███████╗██║██║░╚═╝░██║██║██║░╚███║██║░░██║██║░░██║  ██████╔╝███████╗███████╗
# ╚══════╝╚══════╝╚═╝╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝  ╚═════╝░╚══════╝╚══════╝

# ░█████╗░░█████╗░██████╗░██████╗░░█████╗░
# ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗
# ██║░░╚═╝███████║██████╔╝██████╔╝██║░░██║
# ██║░░██╗██╔══██║██╔══██╗██╔══██╗██║░░██║
# ╚█████╔╝██║░░██║██║░░██║██║░░██║╚█████╔╝
# ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░

@login_required(login_url='/login')
def eliminar_item(request, item_id):
    try:
        config = Configuracion.objects.get(id=1)
        producto = Producto.objects.get(id_producto=item_id)
        carrito_item = CarritoItem.objects.get(producto=producto, usuario=request.user)

        if carrito_item.cantidad > 1:
            # Si la cantidad es mayor que 1, simplemente disminuye en 1 la cantidad
            carrito_item.cantidad -= 1
            carrito_item.save()
        else:
            # Si la cantidad es 1 o menos, elimina el artículo del carrito
            carrito_item.delete()
        
        print("Eliminado con éxito")
    except CarritoItem.DoesNotExist:
        print("El ítem no existe")

    return redirect('caja')




# ░██████╗░███████╗███╗░░██╗███████╗██████╗░░█████╗░██████╗░  ██╗░░░░░░█████╗░
# ██╔════╝░██╔════╝████╗░██║██╔════╝██╔══██╗██╔══██╗██╔══██╗  ██║░░░░░██╔══██╗
# ██║░░██╗░█████╗░░██╔██╗██║█████╗░░██████╔╝███████║██████╔╝  ██║░░░░░███████║
# ██║░░╚██╗██╔══╝░░██║╚████║██╔══╝░░██╔══██╗██╔══██║██╔══██╗  ██║░░░░░██╔══██║
# ╚██████╔╝███████╗██║░╚███║███████╗██║░░██║██║░░██║██║░░██║  ███████╗██║░░██║
# ░╚═════╝░╚══════╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝


@login_required(login_url='/login')
def generar_venta(request, parametro1, parametro2, parametro3, parametro4):
    config = Configuracion.objects.get(id=1)

    try:
        carrito_items = CarritoItem.objects.filter(usuario=request.user)
        
        if carrito_items.exists():
            # Crear una nueva venta
            nueva_venta = Venta(usuario=request.user, total=0, vuelto=parametro4)
            nueva_venta.save()
            
            # Variable para almacenar el total de la venta
            total_venta = Decimal('0.00')

            
            # Agregar productos al modelo VentaProducto
            for item in carrito_items:
                subtotal = item.subtotal()
                total_venta += subtotal
                VentaProducto.objects.create(venta=nueva_venta, producto=item.producto, cantidad=item.cantidad, gramaje=item.gramaje, subtotal=subtotal)
            nueva_venta.total = total_venta
            messages.success(request, 'VENTA INGRESADA CORRECTAMENTE.')
            nueva_venta.save()
            
            # Vaciar el carrito del usuario
            carrito_items.delete()
            parametro3 = float(parametro3)
            total_venta = float(nueva_venta.total)
            monto_efectivo = total_venta - parametro3
            monto_efectivo = abs(float(monto_efectivo))
            if parametro2 == "efectivo":
                nueva_venta.vuelto=monto_efectivo
                nueva_venta.save()

            
            if parametro1 == "venta_con_restante":
                FormaPago.objects.create(venta=nueva_venta, tipo_pago=parametro2, monto=parametro3)
                if monto_efectivo > 0:
                    FormaPago.objects.create(venta=nueva_venta, tipo_pago="efectivo", monto=monto_efectivo)
            elif parametro1 == "venta_sin_restante":
                FormaPago.objects.create(venta=nueva_venta, tipo_pago=parametro2, monto=total_venta)
            
            # Verifica si el método de pago es efectivo y llama a la función abrir_caja_impresora
            if parametro1 == "venta_con_restante" or parametro2 == "efectivo":
                if abrir_caja_impresora():
                    messages.success(request, 'Caja abierta exitosamente.')
                else:
                    messages.error(request, 'Error al abrir la caja. Inténtalo de nuevo.')

            if config.imprimir != 'no':
                imprimir_ultima_id()

            ultima_venta = obtener_ultima_venta()
            vuelto = ultima_venta.vuelto
            if vuelto > 0:
                vuelto = '{:.{}f}'.format(vuelto, config.decimales)
                messages.success(request, f'El vuelto de la venta es {vuelto}')


            return redirect('caja')  # Cambiar por la página deseada
        else:
            # Manejar el caso donde el carrito del usuario está vacío
            pass
    except Exception as e:
        # Manejar excepciones u otros errores
        print(f"Ocurrió un error en generar la venta vista: {e}")
        messages.error(request, f"Ocurrió un error en generar la venta: {e}")
        
    # Redireccionar a la página del carrito si ocurre algún error
    return redirect('caja')  # Cambiar por la página del carrito


# ██╗░░░░░██╗░██████╗████████╗░█████╗░██████╗░  ██╗░░░░░░█████╗░░██████╗
# ██║░░░░░██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ██║░░░░░██╔══██╗██╔════╝
# ██║░░░░░██║╚█████╗░░░░██║░░░███████║██████╔╝  ██║░░░░░███████║╚█████╗░
# ██║░░░░░██║░╚═══██╗░░░██║░░░██╔══██║██╔══██╗  ██║░░░░░██╔══██║░╚═══██╗
# ███████╗██║██████╔╝░░░██║░░░██║░░██║██║░░██║  ███████╗██║░░██║██████╔╝
# ╚══════╝╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝╚═════╝░

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░░██████╗
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗██╔════╝
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║╚█████╗░
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║░╚═══██╗
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║██████╔╝
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░

@login_required(login_url='/login')
def listar_ventas(request):
    # Encuentra la fecha de cierre de la última transacción
    ultima_fecha_cierre = RegistroTransaccion.objects.aggregate(Max('fecha_ingreso'))['fecha_ingreso__max']

    if ultima_fecha_cierre:
        # Filtra las ventas por la fecha de cierre de la última transacción
        ventas = Venta.objects.filter(fecha_hora__gt=ultima_fecha_cierre)
    else:
        # Si no hay transacciones registradas, muestra todas las ventas
        ventas = Venta.objects.all()

    fecha = request.GET.get('fecha')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fin = request.GET.get('hora_fin')

    if fecha:
        # Convierte la fecha de texto a un objeto de fecha
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        # Filtra las ventas por la fecha seleccionada
        ventas = ventas.filter(fecha_hora__date=fecha)

    if hora_inicio and hora_fin:
        # Formatea las horas de inicio y fin en objetos de tiempo
        hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin = datetime.strptime(hora_fin, "%H:%M").time()

        # Filtra las ventas por el rango de horas
        ventas = ventas.filter(fecha_hora__time__range=(hora_inicio, hora_fin))

    # Ordena las ventas en orden descendente por fecha_hora
    ventas = ventas.order_by('-fecha_hora')

    return render(request, 'lista_ventas.html', {'ventas': ventas})



# ██████╗░███████╗████████╗░█████╗░██╗░░░░░██╗░░░░░███████╗  ██████╗░███████╗  ██╗░░░██╗███╗░░██╗░█████╗░
# ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██║░░░░░██║░░░░░██╔════╝  ██╔══██╗██╔════╝  ██║░░░██║████╗░██║██╔══██╗
# ██║░░██║█████╗░░░░░██║░░░███████║██║░░░░░██║░░░░░█████╗░░  ██║░░██║█████╗░░  ██║░░░██║██╔██╗██║███████║
# ██║░░██║██╔══╝░░░░░██║░░░██╔══██║██║░░░░░██║░░░░░██╔══╝░░  ██║░░██║██╔══╝░░  ██║░░░██║██║╚████║██╔══██║
# ██████╔╝███████╗░░░██║░░░██║░░██║███████╗███████╗███████╗  ██████╔╝███████╗  ╚██████╔╝██║░╚███║██║░░██║
# ╚═════╝░╚══════╝░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝  ╚═════╝░╚══════╝  ░╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝


@login_required(login_url='/login')
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    productos_vendidos = VentaProducto.objects.filter(venta=venta)
    formas_pago = FormaPago.objects.filter(venta=venta)
    return render(request, 'detalle_venta.html', {'venta': venta, 'productos_vendidos': productos_vendidos, 'formas_pago': formas_pago})



# ░█████╗░███████╗██████╗░██████╗░░█████╗░██████╗░  ██╗░░░░░░█████╗░  ░█████╗░░█████╗░░░░░░██╗░█████╗░
# ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗  ██║░░░░░██╔══██╗  ██╔══██╗██╔══██╗░░░░░██║██╔══██╗
# ██║░░╚═╝█████╗░░██████╔╝██████╔╝███████║██████╔╝  ██║░░░░░███████║  ██║░░╚═╝███████║░░░░░██║███████║
# ██║░░██╗██╔══╝░░██╔══██╗██╔══██╗██╔══██║██╔══██╗  ██║░░░░░██╔══██║  ██║░░██╗██╔══██║██╗░░██║██╔══██║
# ╚█████╔╝███████╗██║░░██║██║░░██║██║░░██║██║░░██║  ███████╗██║░░██║  ╚█████╔╝██║░░██║╚█████╔╝██║░░██║
# ░╚════╝░╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝  ░╚════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝

@login_required(login_url='/login')
def cerrar_caja(request, monto_en_la_caja):
    caja_diaria = CajaDiaria.objects.get(id=1)
    try:
        ultima_fecha_registro = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
    except RegistroTransaccion.DoesNotExist:
        ultima_fecha_registro = None

    if ultima_fecha_registro:
        ventas_despues_ultima_fecha = Venta.objects.filter(fecha_hora__gte=ultima_fecha_registro)
    else:
        ventas_despues_ultima_fecha = Venta.objects.all()

    # Calcular el total de ventas
    total_ventas_despues_ultima_fecha = ventas_despues_ultima_fecha.aggregate(Sum('total'))['total__sum']

    if total_ventas_despues_ultima_fecha is None:
        total_ventas_despues_ultima_fecha = 0

    # Calcular los montos divididos
    monto_efectivo = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_credito = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='credito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_debito = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_transferencia = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='transferencia').aggregate(Sum('monto'))['monto__sum'] or 0
    

    # Guardar los datos en el modelo RegistroTransaccion
    registro = RegistroTransaccion.objects.create(
        monto_total=total_ventas_despues_ultima_fecha,
        monto_efectivo=monto_efectivo,
        monto_credito=monto_credito,
        monto_debito=monto_debito,
        monto_transferencia=monto_transferencia,
        monto_retiro = caja_diaria.retiro,
        valor_caja_diaria = caja_diaria.monto,
    )


    caja_diaria_nueva = monto_en_la_caja

    caja_diaria.monto = caja_diaria_nueva
    caja_diaria.retiro = 0.0
    caja_diaria.save()

    # Redirigir a la página de informe general
    return redirect('informe_general')


# ░█████╗░░██████╗░██████╗░███████╗░██████╗░░█████╗░██████╗░  ██╗░░░██╗███╗░░██╗
# ██╔══██╗██╔════╝░██╔══██╗██╔════╝██╔════╝░██╔══██╗██╔══██╗  ██║░░░██║████╗░██║
# ███████║██║░░██╗░██████╔╝█████╗░░██║░░██╗░███████║██████╔╝  ██║░░░██║██╔██╗██║
# ██╔══██║██║░░╚██╗██╔══██╗██╔══╝░░██║░░╚██╗██╔══██║██╔══██╗  ██║░░░██║██║╚████║
# ██║░░██║╚██████╔╝██║░░██║███████╗╚██████╔╝██║░░██║██║░░██║  ╚██████╔╝██║░╚███║
# ╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝╚══════╝░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝  ░╚═════╝░╚═╝░░╚══╝

# ██████╗░██████╗░░█████╗░██████╗░██╗░░░██╗░█████╗░████████╗░█████╗░
# ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║░░░██║██╔══██╗╚══██╔══╝██╔══██╗
# ██████╔╝██████╔╝██║░░██║██║░░██║██║░░░██║██║░░╚═╝░░░██║░░░██║░░██║
# ██╔═══╝░██╔══██╗██║░░██║██║░░██║██║░░░██║██║░░██╗░░░██║░░░██║░░██║
# ██║░░░░░██║░░██║╚█████╔╝██████╔╝╚██████╔╝╚█████╔╝░░░██║░░░╚█████╔╝
# ╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚═════╝░░╚═════╝░░╚════╝░░░░╚═╝░░░░╚════╝░

@login_required(login_url='/login')
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guarda el producto en la base de datos
            producto = form.save()
            # Agrega un mensaje de éxito
            messages.success(request, 'Producto creado con éxito.')
            # Redirige a la página de detalles del producto o a donde desees
            return redirect('agregar_producto')  # Cambia 'agregar_producto' por la URL deseada
    else:
        form = ProductoForm()
    
    return render(request, 'agregar_producto.html', {'form': form})

    
    

# ██╗░░░██╗██████╗░██████╗░░█████╗░████████╗███████╗
# ██║░░░██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝
# ██║░░░██║██████╔╝██║░░██║███████║░░░██║░░░█████╗░░
# ██║░░░██║██╔═══╝░██║░░██║██╔══██║░░░██║░░░██╔══╝░░
# ╚██████╔╝██║░░░░░██████╔╝██║░░██║░░░██║░░░███████╗
# ░╚═════╝░╚═╝░░░░░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝


def check_updates(request):
    try:
        with open("update_info.txt", "r") as file:
            lines = file.readlines()

        if lines:
            # La última línea contiene la información más reciente
            last_line = lines[-1]
            parts = last_line.split(' - ')

            stored_version_line = lines[-1].strip()
            stored_version = stored_version_line.split()[-1]
            try:
                # Intentar analizar la cadena de fecha
                fecha_ultima_actualizacion_archivo = datetime.strptime(parts[0].strip(), '%Y-%m-%d %H:%M:%S')
                            # Obtener el objeto ActualizacionModel con id=1
                ultima_actualizacion, created = ActualizacionModel.objects.get_or_create(id=1)

                # Actualizar el objeto con los nuevos datos
                ultima_actualizacion.fecha_actualizacion = fecha_ultima_actualizacion_archivo
                ultima_actualizacion.version = stored_version
                ultima_actualizacion.save()
            except ValueError:
                print("Error al analizar la cadena de fecha. Formato no válido.")
                fecha_ultima_actualizacion_archivo = None

        else:
            print("El archivo está vacío")

    except FileNotFoundError:
        print("El archivo no existe")

    # Repositorio de GitHub y nombre del propietario
    owner = 'gladoncio'
    repo = 'caja_registradora'

    # URL de la API de GitHub para obtener las releases
    api_url = f'https://api.github.com/repos/{owner}/{repo}/releases'

    try:
        # Realizar la solicitud a la API de GitHub
        response = requests.get(api_url)
        response.raise_for_status()  # Asegúrate de que la solicitud fue exitosa
        github_releases = response.json()
    except requests.RequestException as e:
        # Manejar la excepción según sea necesario
        print(f"Error al hacer la solicitud a la API de GitHub: {e}")
        github_releases = []

    # Filtrar solo las releases (excluir drafts y pre-releases)
    github_releases = [release for release in github_releases if isinstance(release, dict) and not release.get('draft') and not release.get('prerelease')]

    if github_releases:
        fecha_ultima_release_github_str = github_releases[0]['published_at']
        fecha_ultima_release_github = datetime.strptime(fecha_ultima_release_github_str, '%Y-%m-%dT%H:%M:%SZ')
        # Convertir la fecha a timezone-aware (UTC)
        fecha_ultima_release_github = fecha_ultima_release_github.replace(tzinfo=timezone.utc)
    else:
        fecha_ultima_release_github = None

    # Obtener la fecha de la última actualización en tu modelo
    ultima_actualizacion = ActualizacionModel.objects.latest('fecha_actualizacion')
    fecha_ultima_actualizacion_modelo = ultima_actualizacion.fecha_actualizacion.replace(tzinfo=timezone.utc) if ultima_actualizacion else None

    # Comparar las fechas
    hay_actualizaciones = fecha_ultima_release_github and (
        not fecha_ultima_actualizacion_modelo or
        fecha_ultima_release_github > fecha_ultima_actualizacion_modelo
    )

    # Determinar el mensaje a mostrar en el template
    mensaje_actualizacion = "¡Estás actualizado!" if not hay_actualizaciones else "Hay actualizaciones disponibles."
    if hay_actualizaciones:
        message = "Las actualizaciones se aplican cada 30 minutos automáticamente."
        messages.success(request, message)

    context = {'hay_actualizaciones': hay_actualizaciones,
               'mensaje_actualizacion': mensaje_actualizacion,
               'releases': github_releases}
    
    return render(request, 'actualizaciones.html', context)




# ░█████╗░██████╗░██████╗░██╗██████╗░  ██╗░░░░░░█████╗░  ░█████╗░░█████╗░░░░░░██╗░█████╗░
# ██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗  ██║░░░░░██╔══██╗  ██╔══██╗██╔══██╗░░░░░██║██╔══██╗
# ███████║██████╦╝██████╔╝██║██████╔╝  ██║░░░░░███████║  ██║░░╚═╝███████║░░░░░██║███████║
# ██╔══██║██╔══██╗██╔══██╗██║██╔══██╗  ██║░░░░░██╔══██║  ██║░░██╗██╔══██║██╗░░██║██╔══██║
# ██║░░██║██████╦╝██║░░██║██║██║░░██║  ███████╗██║░░██║  ╚█████╔╝██║░░██║╚█████╔╝██║░░██║
# ╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝╚═╝░░╚═╝  ╚══════╝╚═╝░░╚═╝  ░╚════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝

# ░█████╗░░█████╗░███╗░░██╗  ░█████╗░██╗░░░░░░█████╗░██╗░░░██╗███████╗
# ██╔══██╗██╔══██╗████╗░██║  ██╔══██╗██║░░░░░██╔══██╗██║░░░██║██╔════╝
# ██║░░╚═╝██║░░██║██╔██╗██║  ██║░░╚═╝██║░░░░░███████║╚██╗░██╔╝█████╗░░
# ██║░░██╗██║░░██║██║╚████║  ██║░░██╗██║░░░░░██╔══██║░╚████╔╝░██╔══╝░░
# ╚█████╔╝╚█████╔╝██║░╚███║  ╚█████╔╝███████╗██║░░██║░░╚██╔╝░░███████╗
# ░╚════╝░░╚════╝░╚═╝░░╚══╝  ░╚════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝

@login_required(login_url='/login')
def abrir_caja(request):
    configuracion = Configuracion.objects.first()
    if request.method == 'POST':
        form = ContraseñaForm(request.POST)
        if form.is_valid():
            # Verifica si la contraseña es correcta
            contraseña = form.cleaned_data['contraseña']
            if contraseña == configuracion.clave_anulacion or contraseña == request.user.clave_anulacion:
                try:
                    # Abre una conexión con la impresora a través de USB (sustituye los valores con los adecuados)
                    abrir_caja_impresora()

                    messages.error(request, 'Caja abierta Exitosamente.')
                except Exception as e:
                    return HttpResponse(f"Error al abrir la caja: {str(e)}", status=500)
            else:
                messages.error(request, 'Contraseña incorrecta. Inténtalo de nuevo.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = ContraseñaForm()

    return render(request, 'abrir_caja.html', {'form': form})


# ░█████╗░██╗░░░░░░█████╗░██╗░░░██╗███████╗  ██████╗░███████╗
# ██╔══██╗██║░░░░░██╔══██╗██║░░░██║██╔════╝  ██╔══██╗██╔════╝
# ██║░░╚═╝██║░░░░░███████║╚██╗░██╔╝█████╗░░  ██║░░██║█████╗░░
# ██║░░██╗██║░░░░░██╔══██║░╚████╔╝░██╔══╝░░  ██║░░██║██╔══╝░░
# ╚█████╔╝███████╗██║░░██║░░╚██╔╝░░███████╗  ██████╔╝███████╗
# ░╚════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝  ╚═════╝░╚══════╝

# ░█████╗░███╗░░██╗██╗░░░██╗██╗░░░░░░█████╗░░█████╗░██╗░█████╗░███╗░░██╗
# ██╔══██╗████╗░██║██║░░░██║██║░░░░░██╔══██╗██╔══██╗██║██╔══██╗████╗░██║
# ███████║██╔██╗██║██║░░░██║██║░░░░░███████║██║░░╚═╝██║██║░░██║██╔██╗██║
# ██╔══██║██║╚████║██║░░░██║██║░░░░░██╔══██║██║░░██╗██║██║░░██║██║╚████║
# ██║░░██║██║░╚███║╚██████╔╝███████╗██║░░██║╚█████╔╝██║╚█████╔╝██║░╚███║
# ╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░╚══════╝╚═╝░░╚═╝░╚════╝░╚═╝░╚════╝░╚═╝░░╚══╝

@login_required(login_url='/login')
def generate_barcode(request):
    configuracion = Configuracion.objects.first()
    barcode_image = None

    if configuracion:
        data = configuracion.clave_anulacion
        # Crea el objeto de código de barras (en este caso, EAN-13)
        code = barcode.get('ean13', data, writer=barcode.writer.ImageWriter())
        # Genera el código de barras como una imagen
        barcode_image = code.render()

        # Convierte la imagen en una secuencia de bytes
        image_bytes = BytesIO()
        barcode_image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()

        # Guarda la imagen en la carpeta de medios
        media_root = settings.MEDIA_ROOT
        image_path = os.path.join(media_root, 'barcode.png')  # Cambia el nombre del archivo si lo deseas
        with open(image_path, 'wb') as image_file:
            image_file.write(image_bytes)

        # Obtén la URL de la imagen generada en la carpeta de medios
        image_url = os.path.join(settings.MEDIA_URL, 'barcode.png')  # Asegúrate de que coincida con la ruta de medios en tu proyecto

    context = {
        'image_url': image_url,  # Pasamos la URL de la imagen al contexto
    }

    return render(request, 'generate_barcode.html', context)



# ░█████╗░██████╗░███████╗░█████╗░██████╗░  ██╗░░░██╗░██████╗██╗░░░██╗░█████╗░██████╗░██╗░█████╗░░██████╗
# ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗  ██║░░░██║██╔════╝██║░░░██║██╔══██╗██╔══██╗██║██╔══██╗██╔════╝
# ██║░░╚═╝██████╔╝█████╗░░███████║██████╔╝  ██║░░░██║╚█████╗░██║░░░██║███████║██████╔╝██║██║░░██║╚█████╗░
# ██║░░██╗██╔══██╗██╔══╝░░██╔══██║██╔══██╗  ██║░░░██║░╚═══██╗██║░░░██║██╔══██║██╔══██╗██║██║░░██║░╚═══██╗
# ╚█████╔╝██║░░██║███████╗██║░░██║██║░░██║  ╚██████╔╝██████╔╝╚██████╔╝██║░░██║██║░░██║██║╚█████╔╝██████╔╝
# ░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝  ░╚═════╝░╚═════╝░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░╚════╝░╚═════╝░


@login_required(login_url='/login')
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            # Verificar si el permiso es "admin"
            permiso = form.cleaned_data['permisos']
            if permiso == 'admin':
                Usuario.objects.create_superuser(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    email='',  # Puedes dejarlo en blanco si no estás usando el campo de correo electrónico
                )
            else:
                form.save()

            messages.success(request, 'Usuario creado exitosamente.')  # Mensaje de éxito
            return redirect('crear_usuario')  # Redirige a la página de éxito después de crear el usuario
        else:
            messages.error(request, 'Ha ocurrido un error. Por favor, revise el formulario.')  # Mensaje de error
    else:
        form = UsuarioCreationForm()

    return render(request, 'crear_usuario.html', {'form': form})


# ██╗███╗░░░███╗██████╗░██████╗░██╗███╗░░░███╗██╗██████╗░  ██████╗░░█████╗░██╗░░░░░███████╗████████╗░█████╗░
# ██║████╗░████║██╔══██╗██╔══██╗██║████╗░████║██║██╔══██╗  ██╔══██╗██╔══██╗██║░░░░░██╔════╝╚══██╔══╝██╔══██╗
# ██║██╔████╔██║██████╔╝██████╔╝██║██╔████╔██║██║██████╔╝  ██████╦╝██║░░██║██║░░░░░█████╗░░░░░██║░░░███████║
# ██║██║╚██╔╝██║██╔═══╝░██╔══██╗██║██║╚██╔╝██║██║██╔══██╗  ██╔══██╗██║░░██║██║░░░░░██╔══╝░░░░░██║░░░██╔══██║
# ██║██║░╚═╝░██║██║░░░░░██║░░██║██║██║░╚═╝░██║██║██║░░██║  ██████╦╝╚█████╔╝███████╗███████╗░░░██║░░░██║░░██║
# ╚═╝╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝╚═╝╚═╝░░╚═╝  ╚═════╝░░╚════╝░╚══════╝╚══════╝░░░╚═╝░░░╚═╝░░╚═╝


@login_required(login_url='/login')
def imprimir_boleta(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)

    # Genera el contenido de la boleta en formato de comandos de impresión para Xprinter XP-80C
    content = generar_comandos_de_impresion(venta)

    # Envía los comandos de impresión a la impresora USB
    imprimir_en_xprinter(content)

    # Devuelve una respuesta vacía o un mensaje de éxito
    return HttpResponse("Boleta impresa exitosamente")






# ░██████╗███████╗██╗░░░░░███████╗░█████╗░░█████╗░██╗░█████╗░███╗░░██╗░█████╗░██████╗░  ███████╗██╗░░░░░
# ██╔════╝██╔════╝██║░░░░░██╔════╝██╔══██╗██╔══██╗██║██╔══██╗████╗░██║██╔══██╗██╔══██╗  ██╔════╝██║░░░░░
# ╚█████╗░█████╗░░██║░░░░░█████╗░░██║░░╚═╝██║░░╚═╝██║██║░░██║██╔██╗██║███████║██████╔╝  █████╗░░██║░░░░░
# ░╚═══██╗██╔══╝░░██║░░░░░██╔══╝░░██║░░██╗██║░░██╗██║██║░░██║██║╚████║██╔══██║██╔══██╗  ██╔══╝░░██║░░░░░
# ██████╔╝███████╗███████╗███████╗╚█████╔╝╚█████╔╝██║╚█████╔╝██║░╚███║██║░░██║██║░░██║  ███████╗███████╗
# ╚═════╝░╚══════╝╚══════╝╚══════╝░╚════╝░░╚════╝░╚═╝░╚════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝  ╚══════╝╚══════╝

# ███╗░░░███╗███████╗████████╗░█████╗░██████╗░░█████╗░  ██████╗░███████╗  ██████╗░░█████╗░░██████╗░░█████╗░
# ████╗░████║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗  ██╔══██╗██╔════╝  ██╔══██╗██╔══██╗██╔════╝░██╔══██╗
# ██╔████╔██║█████╗░░░░░██║░░░██║░░██║██║░░██║██║░░██║  ██║░░██║█████╗░░  ██████╔╝███████║██║░░██╗░██║░░██║
# ██║╚██╔╝██║██╔══╝░░░░░██║░░░██║░░██║██║░░██║██║░░██║  ██║░░██║██╔══╝░░  ██╔═══╝░██╔══██║██║░░╚██╗██║░░██║
# ██║░╚═╝░██║███████╗░░░██║░░░╚█████╔╝██████╔╝╚█████╔╝  ██████╔╝███████╗  ██║░░░░░██║░░██║╚██████╔╝╚█████╔╝
# ╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░░╚════╝░╚═════╝░░╚════╝░  ╚═════╝░╚══════╝  ╚═╝░░░░░╚═╝░░╚═╝░╚═════╝░░╚════╝░

@login_required(login_url='/login')
def seleccionar_metodo_pago(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in carrito_items)
    metodos_pago = ["Efectivo Justo", "Efectivo", "Transferencia", "Débito"]
    if not carrito_items:
        messages.error(request, 'No hay artículos en el carrito.')
        return redirect('caja')  # Reemplaza 'nombre_de_la_vista_caja' con la URL de la vista "caja".
    context = {'metodos_pago': metodos_pago, 'total' : total}
    return render(request, 'seleccionar_pago.html', context)



@login_required(login_url='/login')
def procesar_pago(request):
    if request.method == 'POST':
        metodo_pago_seleccionado = request.POST.get('metodoPago')
        
        if metodo_pago_seleccionado == 'Efectivo':
            # Redirige a la vista para ingresar el monto en efectivo
            return redirect('ingresar_monto_efectivo')
        elif metodo_pago_seleccionado == 'Transferencia':
            # Redirige a la vista generar_venta con los parámetros adecuados para Transferencia
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'transferencia', '0', '0'])
            return redirect(url_generar_venta)
        elif metodo_pago_seleccionado == 'Débito':
            # Redirige a la vista generar_venta con los parámetros adecuados para Débito
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'debito', '0', '0'])
            return redirect(url_generar_venta)
        elif metodo_pago_seleccionado == 'Efectivo Justo':
            # Redirige a la vista generar_venta con los parámetros adecuados para Crédito
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'efectivo', '0', '0'])
            return redirect(url_generar_venta)
    
    # Redirige a una vista predeterminada en caso de error o si no se seleccionó un método de pago válido
    return redirect('caja')  # Cambiar por la página deseada



# ██╗░░░██╗██╗░██████╗████████╗░█████╗░  ██████╗░░█████╗░██████╗░░█████╗░
# ██║░░░██║██║██╔════╝╚══██╔══╝██╔══██╗  ██╔══██╗██╔══██╗██╔══██╗██╔══██╗
# ╚██╗░██╔╝██║╚█████╗░░░░██║░░░███████║  ██████╔╝███████║██████╔╝███████║
# ░╚████╔╝░██║░╚═══██╗░░░██║░░░██╔══██║  ██╔═══╝░██╔══██║██╔══██╗██╔══██║
# ░░╚██╔╝░░██║██████╔╝░░░██║░░░██║░░██║  ██║░░░░░██║░░██║██║░░██║██║░░██║
# ░░░╚═╝░░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝  ╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░░██████╗  ███████╗███╗░░██╗
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗██╔════╝  ██╔════╝████╗░██║
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║╚█████╗░  █████╗░░██╔██╗██║
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║░╚═══██╗  ██╔══╝░░██║╚████║
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║██████╔╝  ███████╗██║░╚███║
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░  ╚══════╝╚═╝░░╚══╝

# ███████╗███████╗███████╗░█████╗░████████╗██╗██╗░░░██╗░█████╗░
# ██╔════╝██╔════╝██╔════╝██╔══██╗╚══██╔══╝██║██║░░░██║██╔══██╗
# █████╗░░█████╗░░█████╗░░██║░░╚═╝░░░██║░░░██║╚██╗░██╔╝██║░░██║
# ██╔══╝░░██╔══╝░░██╔══╝░░██║░░██╗░░░██║░░░██║░╚████╔╝░██║░░██║
# ███████╗██║░░░░░███████╗╚█████╔╝░░░██║░░░██║░░╚██╔╝░░╚█████╔╝
# ╚══════╝╚═╝░░░░░╚══════╝░╚════╝░░░░╚═╝░░░╚═╝░░░╚═╝░░░░╚════╝░


@login_required(login_url='/login')
def ingresar_monto_efectivo(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in carrito_items)

    if request.method == 'POST':
        monto_vuelto = request.POST.get('monto_vuelto', '0.00')
        # Obtener el monto ingresado por el usuario
        monto_efectivo = float(request.POST.get('monto_efectivo', '0'))
        if monto_efectivo >= total:
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'efectivo', monto_efectivo , monto_vuelto])
            return redirect(url_generar_venta)
        else:
            # Redirigir a la vista seleccionar_metodo_pago_resto
            url_seleccionar_metodo_pago_resto = reverse('seleccionar_metodo_pago_resto', args=[total, monto_efectivo])
            return redirect(url_seleccionar_metodo_pago_resto)

    context = {'total': total}
    return render(request, 'ingresar_monto_efectivo.html', context)



# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░  ░█████╗░░█████╗░███╗░░██╗  ███████╗██╗░░░░░
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗  ██╔══██╗██╔══██╗████╗░██║  ██╔════╝██║░░░░░
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║  ██║░░╚═╝██║░░██║██╔██╗██║  █████╗░░██║░░░░░
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║  ██║░░██╗██║░░██║██║╚████║  ██╔══╝░░██║░░░░░
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║  ╚█████╔╝╚█████╔╝██║░╚███║  ███████╗███████╗
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝  ░╚════╝░░╚════╝░╚═╝░░╚══╝  ╚══════╝╚══════╝

# ██████╗░███████╗░██████╗████████╗░█████╗░███╗░░██╗████████╗███████╗
# ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗████╗░██║╚══██╔══╝██╔════╝
# ██████╔╝█████╗░░╚█████╗░░░░██║░░░███████║██╔██╗██║░░░██║░░░█████╗░░
# ██╔══██╗██╔══╝░░░╚═══██╗░░░██║░░░██╔══██║██║╚████║░░░██║░░░██╔══╝░░
# ██║░░██║███████╗██████╔╝░░░██║░░░██║░░██║██║░╚███║░░░██║░░░███████╗
# ╚═╝░░╚═╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝░░░╚═╝░░░╚══════╝


@login_required(login_url='/login')
def seleccionar_metodo_pago_resto(request, total, monto_efectivo):
    total = float(total)
    monto_efectivo = float(monto_efectivo)
    # Verifica si hay un restante por pagar (restante > 0)
    restante = total - monto_efectivo
    context = {'total': total, 'monto_efectivo': monto_efectivo, 'restante': restante}
    if restante <= 0:
        # Si no hay restante, redirige a la página de éxito o la que prefieras
        return redirect('caja')  # Cambia 'pagina_exito' por la URL deseada

    if request.method == 'POST':
        # Obtén el método de pago seleccionado por el usuario
        metodo_pago_seleccionado = request.POST.get('metodoPagoResto')
        print(metodo_pago_seleccionado)
        if metodo_pago_seleccionado == 'volver':
            return redirect('seleccionar_metodo_pago')


        
        # Redirige a la vista para procesar el pago con los parámetros necesarios
        return redirect('procesar_pago_restante', metodo_pago=metodo_pago_seleccionado, restante=restante)

    # De lo contrario, renderiza la página de selección de método de pago
    return render(request, 'seleccionar_metodo_pago_resto.html', context)

@login_required(login_url='/login')
def procesar_pago_restante(request, metodo_pago, restante):
    url_generar_venta = reverse('generar_venta', args=['venta_con_restante', metodo_pago, restante ,'0'])
    return redirect(url_generar_venta)


# ██╗░░░░░██╗░██████╗████████╗░█████╗░██████╗░  ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░░██████╗
# ██║░░░░░██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗██╔════╝
# ██║░░░░░██║╚█████╗░░░░██║░░░███████║██████╔╝  ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║╚█████╗░
# ██║░░░░░██║░╚═══██╗░░░██║░░░██╔══██║██╔══██╗  ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║░╚═══██╗
# ███████╗██║██████╔╝░░░██║░░░██║░░██║██║░░██║  ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║██████╔╝
# ╚══════╝╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝  ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░

# ░█████╗░███╗░░██╗██╗░░░██╗██╗░░░░░░█████╗░██████╗░░█████╗░░██████╗
# ██╔══██╗████╗░██║██║░░░██║██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝
# ███████║██╔██╗██║██║░░░██║██║░░░░░███████║██║░░██║███████║╚█████╗░
# ██╔══██║██║╚████║██║░░░██║██║░░░░░██╔══██║██║░░██║██╔══██║░╚═══██╗
# ██║░░██║██║░╚███║╚██████╔╝███████╗██║░░██║██████╔╝██║░░██║██████╔╝
# ╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═════╝░


@login_required(login_url='/login')
def listar_ventas_respaldo(request):
    # Aquí debes obtener las ventas del modelo VentaRespaldo
    ventas_respaldo = VentaRespaldo.objects.all()  # Puedes personalizar la consulta según tus necesidades

    return render(request, 'lista_ventas_respaldo.html', {'ventas_respaldo': ventas_respaldo})

@login_required(login_url='/login')
def listar_ventas_respaldo(request):
    # Encuentra la fecha de cierre de la última transacción
    ultima_fecha_cierre = RegistroTransaccion.objects.aggregate(Max('fecha_ingreso'))['fecha_ingreso__max']

    if ultima_fecha_cierre:
        # Filtra las ventas por la fecha de cierre de la última transacción
        ventas = VentaRespaldo.objects.filter(fecha_hora__gt=ultima_fecha_cierre)
    else:
        # Si no hay transacciones registradas, muestra todas las ventas
        ventas = VentaRespaldo.objects.all()

    fecha = request.GET.get('fecha')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fin = request.GET.get('hora_fin')

    if fecha:
        # Convierte la fecha de texto a un objeto de fecha
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        # Filtra las ventas por la fecha seleccionada
        ventas = ventas.filter(fecha_hora__date=fecha)

    if hora_inicio and hora_fin:
        # Formatea las horas de inicio y fin en objetos de tiempo
        hora_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin = datetime.strptime(hora_fin, "%H:%M").time()

        # Filtra las ventas por el rango de horas
        ventas = ventas.filter(fecha_hora__time__range=(hora_inicio, hora_fin))

    return render(request, 'lista_ventas_respaldo.html', {'ventas': ventas})


# ██████╗░███████╗████████╗░█████╗░██╗░░░░░██╗░░░░░███████╗  ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░
# ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██║░░░░░██║░░░░░██╔════╝  ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗
# ██║░░██║█████╗░░░░░██║░░░███████║██║░░░░░██║░░░░░█████╗░░  ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║
# ██║░░██║██╔══╝░░░░░██║░░░██╔══██║██║░░░░░██║░░░░░██╔══╝░░  ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║
# ██████╔╝███████╗░░░██║░░░██║░░██║███████╗███████╗███████╗  ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║
# ╚═════╝░╚══════╝░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝  ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝

# ░█████╗░███╗░░██╗██╗░░░██╗██╗░░░░░░█████╗░██████╗░░█████╗░
# ██╔══██╗████╗░██║██║░░░██║██║░░░░░██╔══██╗██╔══██╗██╔══██╗
# ███████║██╔██╗██║██║░░░██║██║░░░░░███████║██║░░██║███████║
# ██╔══██║██║╚████║██║░░░██║██║░░░░░██╔══██║██║░░██║██╔══██║
# ██║░░██║██║░╚███║╚██████╔╝███████╗██║░░██║██████╔╝██║░░██║
# ╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝


@login_required(login_url='/login')
def detalle_venta_respaldo(request, venta_respaldo_id):
    venta_respaldo = get_object_or_404(VentaRespaldo, id=venta_respaldo_id)
    productos_vendidos = VentaProductoRespaldo.objects.filter(venta=venta_respaldo)
    formas_pago = FormaPagoRespaldo.objects.filter(venta=venta_respaldo)
    return render(request, 'detalle_venta_respaldo.html', {'venta_respaldo': venta_respaldo, 'productos_vendidos': productos_vendidos, 'formas_pago': formas_pago})



# ███████╗██╗░░░░░██╗███╗░░░███╗██╗███╗░░██╗░█████╗░██████╗░  ██╗░░░██╗███╗░░██╗░█████╗░
# ██╔════╝██║░░░░░██║████╗░████║██║████╗░██║██╔══██╗██╔══██╗  ██║░░░██║████╗░██║██╔══██╗
# █████╗░░██║░░░░░██║██╔████╔██║██║██╔██╗██║███████║██████╔╝  ██║░░░██║██╔██╗██║███████║
# ██╔══╝░░██║░░░░░██║██║╚██╔╝██║██║██║╚████║██╔══██║██╔══██╗  ██║░░░██║██║╚████║██╔══██║
# ███████╗███████╗██║██║░╚═╝░██║██║██║░╚███║██║░░██║██║░░██║  ╚██████╔╝██║░╚███║██║░░██║
# ╚══════╝╚══════╝╚═╝╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝  ░╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝

@login_required(login_url='/login')
def eliminar_venta(request, venta_id):
    config = Configuracion.objects.get(id=1)
    venta = get_object_or_404(Venta, id=venta_id)

    if request.method == 'POST':
        # Obtén la contraseña proporcionada por el usuario
        contraseña = request.POST.get('contraseña')

        # Verifica si la contraseña coincide
        if contraseña == config.clave_anulacion or contraseña == request.user.clave_anulacion:
            # Elimina la venta
            venta.delete()
            messages.success(request, 'Venta eliminada exitosamente.')
            return redirect('listar_ventas')
        else:
            # Contraseña incorrecta, muestra un mensaje de error
            messages.error(request, 'Contraseña incorrecta. La venta no se ha eliminado.')

    return redirect('listar_ventas')

# ██╗███╗░░██╗███████╗░█████╗░██████╗░███╗░░░███╗███████╗  ░██████╗░███████╗███╗░░██╗███████╗██████╗░░█████╗░██╗░░░░░
# ██║████╗░██║██╔════╝██╔══██╗██╔══██╗████╗░████║██╔════╝  ██╔════╝░██╔════╝████╗░██║██╔════╝██╔══██╗██╔══██╗██║░░░░░
# ██║██╔██╗██║█████╗░░██║░░██║██████╔╝██╔████╔██║█████╗░░  ██║░░██╗░█████╗░░██╔██╗██║█████╗░░██████╔╝███████║██║░░░░░
# ██║██║╚████║██╔══╝░░██║░░██║██╔══██╗██║╚██╔╝██║██╔══╝░░  ██║░░╚██╗██╔══╝░░██║╚████║██╔══╝░░██╔══██╗██╔══██║██║░░░░░
# ██║██║░╚███║██║░░░░░╚█████╔╝██║░░██║██║░╚═╝░██║███████╗  ╚██████╔╝███████╗██║░╚███║███████╗██║░░██║██║░░██║███████╗
# ╚═╝╚═╝░░╚══╝╚═╝░░░░░░╚════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝  ░╚═════╝░╚══════╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝

@login_required(login_url='/login')
def informe_general(request):
    caja_diaria = CajaDiaria.objects.get(id=1)
    config = Configuracion.objects.get(id=1)
    decimales = config.decimales
    try:
        # Obtener la última fecha de RegistroTransaccion si existe
        ultima_fecha_registro = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
    except RegistroTransaccion.DoesNotExist:
        ultima_fecha_registro = None

    # Filtrar todas las ventas después de la última fecha de RegistroTransaccion si existe, o todas las ventas si no existe
    if ultima_fecha_registro:
        ventas_despues_ultima_fecha = Venta.objects.filter(fecha_hora__gte=ultima_fecha_registro)
    else:
        ventas_despues_ultima_fecha = Venta.objects.all()

    # Calcular el total de ventas
    total_ventas_despues_ultima_fecha = ventas_despues_ultima_fecha.aggregate(Sum('total'))['total__sum'] or 0

    # Calcular los montos divididos
    monto_efectivo = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_credito = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='credito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_debito = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_transferencia = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='transferencia').aggregate(Sum('monto'))['monto__sum'] or 0

    # Filtrar los gastos después de la última fecha de RegistroTransaccion
    if ultima_fecha_registro:
        gastos_despues_ultima_fecha = GastoCaja.objects.filter(fecha_hora__gte=ultima_fecha_registro)
    else:
        gastos_despues_ultima_fecha = GastoCaja.objects.all()

    # Calcular el total de gastos
    total_gastos_despues_ultima_fecha = gastos_despues_ultima_fecha.aggregate(Sum('monto'))['monto__sum'] or 0

    ventas_por_departamento = VentaProducto.objects.filter(venta__in=ventas_despues_ultima_fecha).values('producto__departamento__nombre').annotate(
        departamento=F('producto__departamento__nombre'),  # Copia el nombre del departamento
        total_ventas=Sum('subtotal')
    )

    # Luego, calcula el total bruto general solo para estas ventas filtradas
    total_bruto_general = VentaProducto.objects.filter(venta__in=ventas_despues_ultima_fecha).aggregate(
        total_bruto=ExpressionWrapper(
            Sum(F('producto__precio') * F('cantidad'), output_field=DecimalField(max_digits=10, decimal_places=2)),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        total_neto=Sum(F('subtotal'), output_field=DecimalField(max_digits=10, decimal_places=2))
    )
    
    monto_que_deberia_dar = monto_efectivo + caja_diaria.monto - caja_diaria.retiro - total_gastos_despues_ultima_fecha

    context = {
        'total_ventas_despues_ultima_fecha': total_ventas_despues_ultima_fecha,
        'monto_efectivo': monto_efectivo,
        'monto_credito': monto_credito,
        'monto_debito': monto_debito,
        'monto_transferencia': monto_transferencia,
        'monto_retiro': caja_diaria.retiro,
        'monto_caja': caja_diaria.monto,
        'total_bruto_general': total_bruto_general,
        'ventas_por_departamento': ventas_por_departamento,
        'gastos' : total_gastos_despues_ultima_fecha,
        'caja_que_deberia' :  monto_que_deberia_dar,
    }

    def generar_comandos_de_impresion(context, decimales):
        # Inicializa una cadena vacía para almacenar los comandos de impresión
        content = ""
        content += "--------------------------\n"
        content += "Reporte\n"
        content += "Fecha: {}\n".format(timezone.now().strftime('%Y-%m-%d %H:%M:%S'))
        content += "--------------------------\n"
        
        content += "Ventas del día.\n"
        content += "Total en Efectivo: ${:.{}f}\n".format(context['monto_efectivo'] if context['monto_efectivo'] is not None else 0, decimales)
        content += "Total en Débito: ${:.{}f}\n".format(context['monto_debito'] if context['monto_debito'] is not None else 0, decimales)
        content += "Total en Transferencia: ${:.{}f}\n".format(context['monto_transferencia'] if context['monto_transferencia'] is not None else 0, decimales)
        content += "Total de Retiro: ${:.{}f}\n".format(context['monto_retiro'] if context['monto_retiro'] is not None else 0, decimales)
        content += "Total de gastos: ${:.{}f}\n".format(context['gastos'] if context['gastos'] is not None else 0, decimales)
        content += "Caja Diaria: ${:.{}f}\n".format(context['monto_caja'] if context['monto_caja'] is not None else 0, decimales)
        content += "Total Neto General: ${:.{}f}\n".format(context['total_bruto_general']['total_neto'] if context['total_bruto_general']['total_neto'] is not None else 0, decimales)
      
        content += "Total de Ventas por Depto:\n"
        for venta_por_departamento in ventas_por_departamento:
            content += "{}:\n".format(venta_por_departamento['departamento'] if venta_por_departamento['departamento'] is not None else "sin departamento")
            content += "    ${:.2f}\n".format(venta_por_departamento['total_ventas'] if venta_por_departamento['total_ventas'] is not None else 0.00)
        content += "Total efectivo (restando gastos y retiros): ${:.{}f}\n".format(context['caja_que_deberia'] if context['caja_que_deberia'] is not None else 0, decimales)
      
        content += "--------------------------\n"
        return content
    
    content = generar_comandos_de_impresion(context, decimales)

    # response = HttpResponse(content, content_type='text/plain')

    # imprimir_en_xprinter(content)
    # return response
    if request.method == 'POST':
        print("imprimiendo reporte")
        try:
            imprimir_en_xprinter(content)
        except:
            pass

    return render(request, 'informe_general.html', context)


# ░█████╗░██╗░░░██╗░█████╗░██████╗░██████╗░░█████╗░██████╗░
# ██╔══██╗██║░░░██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗
# ██║░░╚═╝██║░░░██║███████║██║░░██║██████╔╝███████║██████╔╝
# ██║░░██╗██║░░░██║██╔══██║██║░░██║██╔══██╗██╔══██║██╔══██╗
# ╚█████╔╝╚██████╔╝██║░░██║██████╔╝██║░░██║██║░░██║██║░░██║
# ░╚════╝░░╚═════╝░╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝

@login_required(login_url='/login')
def cuadrar(request):
    config = Configuracion.objects.get(id=1)
    decimales = config.decimales
    caja_diaria = CajaDiaria.objects.get(id=1)
    abrir_caja_impresora()
    
    if request.method == 'POST':
        form = BilletesMonedasForm(request.POST)
        if form.is_valid():
            # Procesa los datos ingresados en el formulario
            monedas_10 = form.cleaned_data['monedas_10']
            monedas_50 = form.cleaned_data['monedas_50']
            monedas_100 = form.cleaned_data['monedas_100']
            monedas_500 = form.cleaned_data['monedas_500']
            billetes_1000 = form.cleaned_data['billetes_1000']
            billetes_2000 = form.cleaned_data['billetes_2000']
            billetes_5000 = form.cleaned_data['billetes_5000']
            billetes_10000 = form.cleaned_data['billetes_10000']
            billetes_20000 = form.cleaned_data['billetes_20000']
            maquinas_debito = form.cleaned_data['maquinas_debito']
            
            total_efectivo = (
                monedas_10 + monedas_50 + monedas_100 + monedas_500 +
                billetes_1000 + billetes_2000 + billetes_5000 +
                billetes_10000 + billetes_20000
            )

            try:
                ultima_fecha_registro = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
            except RegistroTransaccion.DoesNotExist:
                ultima_fecha_registro = None

            if ultima_fecha_registro:
                ventas_despues_ultima_fecha = Venta.objects.filter(fecha_hora__gte=ultima_fecha_registro)
            else:
                ventas_despues_ultima_fecha = Venta.objects.all()

                # Filtrar los gastos después de la última fecha de RegistroTransaccion
            if ultima_fecha_registro:
                gastos_despues_ultima_fecha = GastoCaja.objects.filter(fecha_hora__gte=ultima_fecha_registro)
            else:
                gastos_despues_ultima_fecha = GastoCaja.objects.all()

            # Calcular el total de gastos
            total_gastos_despues_ultima_fecha = gastos_despues_ultima_fecha.aggregate(Sum('monto'))['monto__sum'] or 0


            # Calcular los montos divididos
            monto_efectivo = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
            monto_credito = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='credito').aggregate(Sum('monto'))['monto__sum'] or 0
            monto_debito = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
            monto_transferencia = FormaPago.objects.filter(venta__in=ventas_despues_ultima_fecha, tipo_pago='transferencia').aggregate(Sum('monto'))['monto__sum'] or 0
                # Filtrar los gastos después de la última fecha de RegistroTransaccion
            if ultima_fecha_registro:
                gastos_despues_ultima_fecha = GastoCaja.objects.filter(fecha_hora__gte=ultima_fecha_registro)
            else:
                gastos_despues_ultima_fecha = GastoCaja.objects.all()

            # Calcular el total de gastos
            total_gastos_despues_ultima_fecha = gastos_despues_ultima_fecha.aggregate(Sum('monto'))['monto__sum'] or 0


            monto_que_deberia_dar = monto_efectivo + caja_diaria.monto - caja_diaria.retiro - total_gastos_despues_ultima_fecha
            
            cuadre = Cuadre.objects.create(
                usuario=request.user,
                fecha_ingreso=timezone.now(),
                # Otra información que quieras guardar en el modelo Cuadre
            )

            ventas_por_departamento = VentaProducto.objects.filter(venta__in=ventas_despues_ultima_fecha).values('producto__departamento__nombre').annotate(
                departamento=F('producto__departamento__nombre'),  # Copia el nombre del departamento
                total_ventas=Sum('subtotal')
            )


            # Luego, calcula el total bruto general solo para estas ventas filtradas
            total_bruto_general = VentaProducto.objects.filter(venta__in=ventas_despues_ultima_fecha).aggregate(
                total_bruto=ExpressionWrapper(
                    Sum(F('producto__precio') * F('cantidad'), output_field=DecimalField(max_digits=10, decimal_places=2)),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                total_neto=Sum(F('subtotal'), output_field=DecimalField(max_digits=10, decimal_places=2))
            )


            monto_faltante_efectivo = (monto_que_deberia_dar - total_efectivo)
            estado = "faltante"
            if (monto_faltante_efectivo < 0 ):
                estado = "sobrante"

            maquina_faltante = (monto_debito - maquinas_debito)

            context = {
                'total_ventas_despues_ultima_fecha': total_gastos_despues_ultima_fecha,
                'monto_efectivo': monto_efectivo,
                'monto_credito': monto_credito,
                'monto_debito': monto_debito,
                'estado' : estado,
                'monto_transferencia': monto_transferencia,
                'monto_retiro': caja_diaria.retiro,
                'monto_caja': caja_diaria.monto,
                'total_bruto_general': total_bruto_general,
                'ventas_por_departamento': ventas_por_departamento,
                'caja_que_deberia' :  monto_que_deberia_dar,
                'total_gastos_despues_ultima_fecha' : total_gastos_despues_ultima_fecha,
                'monto_en_la_caja' : total_efectivo,
                'efectivo_faltante' : monto_faltante_efectivo,
                'monto_faltante_maquinas' : maquina_faltante,
                'gastos_detalle' : gastos_despues_ultima_fecha,
                'billetes': {
                    'monedas_10': monedas_10,
                    'monedas_50': monedas_50,
                    'monedas_100': monedas_100,
                    'monedas_500': monedas_500,
                    'billetes_1000': billetes_1000,
                    'billetes_2000': billetes_2000,
                    'billetes_5000': billetes_5000,
                    'billetes_10000': billetes_10000,
                    'billetes_20000': billetes_20000,
                }
            }


            def generar_comandos_de_impresion(context, decimales):
                # Inicializa una cadena vacía para almacenar los comandos de impresión
                content = ""
                content += "--------------------------\n"
                content += "Informe de Cierre de Caja\n"
                content += "Fecha: {}\n".format(timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S'))
                content += "--------------------------\n"

                  # Agregar el detalle de billetes
                content += "Detalle de Billetes:\n"
                content += "Monedas de 10: {}\n".format(request.POST.get('monedas_10', 0))
                content += "Monedas de 50: {}\n".format(request.POST.get('monedas_50', 0))
                content += "Monedas de 100: {}\n".format(request.POST.get('monedas_100', 0))
                content += "Monedas de 500: {}\n".format(request.POST.get('monedas_500', 0))
                content += "Billetes de 1000: {}\n".format(request.POST.get('billetes_1000', 0))
                content += "Billetes de 2000: {}\n".format(request.POST.get('billetes_2000', 0))
                content += "Billetes de 5000: {}\n".format(request.POST.get('billetes_5000', 0))
                content += "Billetes de 10000: {}\n".format(request.POST.get('billetes_10000', 0))
                content += "Billetes de 20000: {}\n".format(request.POST.get('billetes_20000', 0))
                content += "--------------------------\n"

                
                # Datos de ventas y montos
                content += "Ventas del día.\n"
                content += "Total en Efectivo: ${:.{}f}\n".format(context['monto_efectivo'] if context['monto_efectivo'] is not None else 0, decimales)
                content += "Total en Débito: ${:.{}f}\n".format(context['monto_debito'] if context['monto_debito'] is not None else 0, decimales)
                content += "Total en Transferencia: ${:.{}f}\n".format(context['monto_transferencia'] if context['monto_transferencia'] is not None else 0, decimales)
                content += "Total de Retiro: ${:.{}f}\n".format(context['monto_retiro'] if context['monto_retiro'] is not None else 0, decimales)
                content += "Total de gastos: ${:.{}f}\n".format(context['total_gastos_despues_ultima_fecha'] if context['total_gastos_despues_ultima_fecha'] is not None else 0, decimales)
                content += "--------------------------\n"

                
                content += "Detalle de los Gastos:\n"
                for gasto in context['gastos_detalle']:
                    # Ajusta la zona horaria si es necesario
                    fecha_en_zona_horaria = timezone.localtime(gasto.fecha_hora)

                    # Utiliza strftime para formatear la fecha
                    fecha_formateada = fecha_en_zona_horaria.strftime('%H:%M')
                    
                    content += "{}\n ${:.0f} - {}\n".format(fecha_formateada, gasto.monto, gasto.descripcion)
                content += "--------------------------\n"

                
                content += "Caja Diaria: ${:.{}f}\n".format(context['monto_caja'] if context['monto_caja'] is not None else 0, decimales)
                content += "Total Neto General: ${:.{}f}\n".format(context['total_bruto_general']['total_neto'] if context['total_bruto_general']['total_neto'] is not None else 0, decimales)
              
                content += "Total de Ventas por Departamento:\n"

                for venta_por_departamento in ventas_por_departamento:
                    content += "{}:\n".format(venta_por_departamento['departamento'] if venta_por_departamento['departamento'] is not None else "sin departamento")
                    content += "    ${:.2f}\n".format(venta_por_departamento['total_ventas'] if venta_por_departamento['total_ventas'] is not None else 0.00)

                content += "Total efectivo (restando gastos y retiros): ${:.{}f}\n".format(context['caja_que_deberia'] if context['caja_que_deberia'] is not None else 0, decimales)
                content += "Efectivo en la Caja: ${:.{}f}\n".format(context['monto_en_la_caja'] if context.get('monto_en_la_caja') is not None else 0, decimales)
                if context['efectivo_faltante'] == 0:
                    content += "El monto cuadra con las ventas ingresadas.\n"
                elif context['efectivo_faltante']>0:
                    content += "Efectivo Faltante: ${:.{}f}\n".format(context['efectivo_faltante'] if context['efectivo_faltante'] is not None else 0, decimales)
                else:
                    context['efectivo_faltante'] = abs(context['efectivo_faltante'])
                    content += "Efectivo Sobrante: ${:.{}f}\n".format(context['efectivo_faltante'] if context['efectivo_faltante'] is not None else 0, decimales)
                content += "Débito Faltante en Máquinas: ${:.{}f}\n".format(context['monto_faltante_maquinas'] if context['monto_faltante_maquinas'] is not None else 0, decimales)
                content += "--------------------------\n"

                return content

        
            content = generar_comandos_de_impresion(context, decimales)

            # response = HttpResponse(content, content_type='text/plain')
            # return response
            try:
                imprimir_en_xprinter(content)
            except:
                pass


            return render(request, 'resultado_cuadre.html', context)
    else:
        form = BilletesMonedasForm()

    return render(request, 'cerrar_caja.html', {'form': form})


# ██╗░░░░░██╗░██████╗████████╗░█████╗░██████╗░  ██╗░░░░░░█████╗░░██████╗
# ██║░░░░░██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ██║░░░░░██╔══██╗██╔════╝
# ██║░░░░░██║╚█████╗░░░░██║░░░███████║██████╔╝  ██║░░░░░██║░░██║╚█████╗░
# ██║░░░░░██║░╚═══██╗░░░██║░░░██╔══██║██╔══██╗  ██║░░░░░██║░░██║░╚═══██╗
# ███████╗██║██████╔╝░░░██║░░░██║░░██║██║░░██║  ███████╗╚█████╔╝██████╔╝
# ╚══════╝╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝  ╚══════╝░╚════╝░╚═════╝░

# ░██████╗░░█████╗░░██████╗████████╗░█████╗░░██████╗
# ██╔════╝░██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝
# ██║░░██╗░███████║╚█████╗░░░░██║░░░██║░░██║╚█████╗░
# ██║░░╚██╗██╔══██║░╚═══██╗░░░██║░░░██║░░██║░╚═══██╗
# ╚██████╔╝██║░░██║██████╔╝░░░██║░░░╚█████╔╝██████╔╝
# ░╚═════╝░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░░╚════╝░╚═════╝░

@login_required(login_url='/login')
def lista_gastos(request):
    try:
        # Obtener la última fecha de RegistroTransaccion si existe
        ultima_fecha_registro = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
    except RegistroTransaccion.DoesNotExist:
        ultima_fecha_registro = None
        gastos_post_ultima_transaccion = GastoCaja.objects.all()

    # Filtrar los gastos que ocurrieron después de la última fecha de RegistroTransaccion si existe
    gastos_post_ultima_transaccion = GastoCaja.objects.filter(fecha_hora__gte=ultima_fecha_registro) if ultima_fecha_registro else None
    if ultima_fecha_registro:
        print("si")
    else:
        gastos_post_ultima_transaccion = GastoCaja.objects.all()
    
    # Filtrar las ventas que ocurrieron después de la última fecha de RegistroTransaccion si existe
    ventas_post_ultima_transaccion = Venta.objects.filter(fecha_hora__gte=ultima_fecha_registro) if ultima_fecha_registro else None

    return render(request, 'lista_gastos.html', {'gastos_post_ultima_transaccion': gastos_post_ultima_transaccion, 'ventas_post_ultima_transaccion': ventas_post_ultima_transaccion})


# ██╗░░░██╗██████╗░██████╗░░█████╗░████████╗███████╗
# ██║░░░██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝
# ██║░░░██║██████╔╝██║░░██║███████║░░░██║░░░█████╗░░
# ██║░░░██║██╔═══╝░██║░░██║██╔══██║░░░██║░░░██╔══╝░░
# ╚██████╔╝██║░░░░░██████╔╝██║░░██║░░░██║░░░███████╗
# ░╚═════╝░╚═╝░░░░░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝

# ░█████╗░░█████╗░███╗░░██╗███████╗██╗░██████╗░██╗░░░██╗██████╗░░█████╗░░█████╗░██╗░█████╗░███╗░░██╗
# ██╔══██╗██╔══██╗████╗░██║██╔════╝██║██╔════╝░██║░░░██║██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗████╗░██║
# ██║░░╚═╝██║░░██║██╔██╗██║█████╗░░██║██║░░██╗░██║░░░██║██████╔╝███████║██║░░╚═╝██║██║░░██║██╔██╗██║
# ██║░░██╗██║░░██║██║╚████║██╔══╝░░██║██║░░╚██╗██║░░░██║██╔══██╗██╔══██║██║░░██╗██║██║░░██║██║╚████║
# ╚█████╔╝╚█████╔╝██║░╚███║██║░░░░░██║╚██████╔╝╚██████╔╝██║░░██║██║░░██║╚█████╔╝██║╚█████╔╝██║░╚███║
# ░╚════╝░░╚════╝░╚═╝░░╚══╝╚═╝░░░░░╚═╝░╚═════╝░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░╚════╝░╚═╝░░╚══╝

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['decimales', 'clave_anulacion', 'idioma', 'imprimir', 'tipo_venta', 'porcentaje_iva', 'tamano_letra']
        widgets = {
            'decimales': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'clave_anulacion': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'idioma': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'imprimir': forms.Select(attrs={'class': 'form-control resize-text onlyinput'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-control resize-text onlyinput'}),
            'porcentaje_iva': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'tamano_letra': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
        }

class ConfiguracionUpdateView(UpdateView):
    model = Configuracion
    form_class = ConfiguracionForm
    template_name = 'edit_configuracion.html'

    def get_object(self, queryset=None):
        return Configuracion.objects.get(pk=1)

    def get_success_url(self):
        return reverse_lazy('config')

# ░██████╗███████╗░█████╗░░█████╗░██╗░█████╗░███╗░░██╗  ██████╗░███████╗
# ██╔════╝██╔════╝██╔══██╗██╔══██╗██║██╔══██╗████╗░██║  ██╔══██╗██╔════╝
# ╚█████╗░█████╗░░██║░░╚═╝██║░░╚═╝██║██║░░██║██╔██╗██║  ██║░░██║█████╗░░
# ░╚═══██╗██╔══╝░░██║░░██╗██║░░██╗██║██║░░██║██║╚████║  ██║░░██║██╔══╝░░
# ██████╔╝███████╗╚█████╔╝╚█████╔╝██║╚█████╔╝██║░╚███║  ██████╔╝███████╗
# ╚═════╝░╚══════╝░╚════╝░░╚════╝░╚═╝░╚════╝░╚═╝░░╚══╝  ╚═════╝░╚══════╝

# ██╗░░░██╗░██████╗██╗░░░██╗░█████╗░██████╗░██╗░█████╗░░██████╗
# ██║░░░██║██╔════╝██║░░░██║██╔══██╗██╔══██╗██║██╔══██╗██╔════╝
# ██║░░░██║╚█████╗░██║░░░██║███████║██████╔╝██║██║░░██║╚█████╗░
# ██║░░░██║░╚═══██╗██║░░░██║██╔══██║██╔══██╗██║██║░░██║░╚═══██╗
# ╚██████╔╝██████╔╝╚██████╔╝██║░░██║██║░░██║██║╚█████╔╝██████╔╝
# ░╚═════╝░╚═════╝░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░╚════╝░╚═════╝░

@login_required(login_url='/login')
def cambiar_clave_usuario(request, user_id):
    user = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        form = CambiarClaveForm(request.POST)
        if form.is_valid():
            nueva_clave = form.cleaned_data['nueva_clave']
            user.set_password(nueva_clave)
            user.save()
            update_session_auth_hash(request, user)  # Actualiza la sesión de autenticación
            messages.success(request, 'La clave se cambió con éxito.')
            return redirect('cambiar_clave_usuario', user_id=user.id)
    else:
        form = CambiarClaveForm()

    return render(request, 'cambiar_clave.html', {'form': form, 'user': user}) 

@login_required(login_url='/login')
def lista_usuarios(request):
    usuarios = Usuario.objects.filter(is_active=True)
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

@login_required(login_url='/login')
def lista_usuarios_desabilitados(request):
    usuarios = Usuario.objects.filter(is_active=False)
    return render(request, 'lista_usuarios_desabilitados.html', {'usuarios': usuarios})


@login_required(login_url='/login')
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    
    usuario.is_active = False

    usuario.save()
        
    messages.success(request, f'El usuario {usuario.username} ha sido eliminado.')
    
    return redirect('lista_usuarios')  # Siempre redirige a la vista de lista de usuarios, incluso si no se elimina el usuario.

@login_required(login_url='/login')
def activar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    
    usuario.is_active = True

    usuario.save()
        
    messages.success(request, f'El usuario {usuario.username} ha sido reactivado.')
    
    return redirect('lista_usuarios')





# ██╗███╗░░░███╗██████╗░██████╗░██╗███╗░░░███╗██╗██████╗░
# ██║████╗░████║██╔══██╗██╔══██╗██║████╗░████║██║██╔══██╗
# ██║██╔████╔██║██████╔╝██████╔╝██║██╔████╔██║██║██████╔╝
# ██║██║╚██╔╝██║██╔═══╝░██╔══██╗██║██║╚██╔╝██║██║██╔══██╗
# ██║██║░╚═╝░██║██║░░░░░██║░░██║██║██║░╚═╝░██║██║██║░░██║
# ╚═╝╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝╚═╝╚═╝░░╚═╝

# ░█████╗░░█████╗░██████╗░██╗░██████╗░░█████╗░  ██████╗░░█████╗░███╗░░░███╗██████╗░░█████╗░███╗░░░███╗
# ██╔══██╗██╔══██╗██╔══██╗██║██╔════╝░██╔══██╗  ██╔══██╗██╔══██╗████╗░████║██╔══██╗██╔══██╗████╗░████║
# ██║░░╚═╝██║░░██║██║░░██║██║██║░░██╗░██║░░██║  ██████╔╝███████║██╔████╔██║██║░░██║██║░░██║██╔████╔██║
# ██║░░██╗██║░░██║██║░░██║██║██║░░╚██╗██║░░██║  ██╔══██╗██╔══██║██║╚██╔╝██║██║░░██║██║░░██║██║╚██╔╝██║
# ╚█████╔╝╚█████╔╝██████╔╝██║╚██████╔╝╚█████╔╝  ██║░░██║██║░░██║██║░╚═╝░██║██████╔╝╚█████╔╝██║░╚═╝░██║
# ░╚════╝░░╚════╝░╚═════╝░╚═╝░╚═════╝░░╚════╝░  ╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚═════╝░░╚════╝░╚═╝░░░░░╚═╝


@login_required(login_url='/login')
def generar_codigo_ean13(request):
    # Genera un número aleatorio de 12 dígitos para el código de barras
    codigo_de_barras = ''.join([str(random.randint(0, 9)) for _ in range(12)])

    # Agrega el dígito de verificación del código EAN-13
    codigo_ean13 = codigo_de_barras + str(EAN13(codigo_de_barras).calculate_checksum())

    # Crea el objeto EAN-13
    ean = EAN13(codigo_ean13, writer=ImageWriter())

    # Genera el código de barras como una imagen PNG
    barcode_image = ean.render()

    # Devuelve la imagen como respuesta HTTP
    response = HttpResponse(content_type='image/png')
    barcode_image.save(response, 'PNG')

    return response




# ██╗░░░██╗███████╗██████╗░  ░█████╗░░█████╗░███╗░░██╗████████╗███████╗██╗░░██╗████████╗░█████╗░  ██████╗░███████╗
# ██║░░░██║██╔════╝██╔══██╗  ██╔══██╗██╔══██╗████╗░██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗  ██╔══██╗██╔════╝
# ╚██╗░██╔╝█████╗░░██████╔╝  ██║░░╚═╝██║░░██║██╔██╗██║░░░██║░░░█████╗░░░╚███╔╝░░░░██║░░░██║░░██║  ██║░░██║█████╗░░
# ░╚████╔╝░██╔══╝░░██╔══██╗  ██║░░██╗██║░░██║██║╚████║░░░██║░░░██╔══╝░░░██╔██╗░░░░██║░░░██║░░██║  ██║░░██║██╔══╝░░
# ░░╚██╔╝░░███████╗██║░░██║  ╚█████╔╝╚█████╔╝██║░╚███║░░░██║░░░███████╗██╔╝╚██╗░░░██║░░░╚█████╔╝  ██████╔╝███████╗
# ░░░╚═╝░░░╚══════╝╚═╝░░╚═╝  ░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░  ╚═════╝░╚══════╝

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝

@login_required(login_url='/login')
def vista_boleta_venta_texto(request, venta_id):
    # Obtén el objeto Venta
    venta = Venta.objects.get(id=venta_id)

    # Llama a la función para generar el contenido
    content = generar_comandos_de_impresion(venta)

    # Devuelve el contenido en texto plano
    response = HttpResponse(content, content_type='text/plain')
    return response



# ██╗░░░██╗░█████╗░░█████╗░██╗░█████╗░██████╗░  ░█████╗░░█████╗░██████╗░██████╗░██╗████████╗░█████╗░
# ██║░░░██║██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗  ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
# ╚██╗░██╔╝███████║██║░░╚═╝██║███████║██████╔╝  ██║░░╚═╝███████║██████╔╝██████╔╝██║░░░██║░░░██║░░██║
# ░╚████╔╝░██╔══██║██║░░██╗██║██╔══██║██╔══██╗  ██║░░██╗██╔══██║██╔══██╗██╔══██╗██║░░░██║░░░██║░░██║
# ░░╚██╔╝░░██║░░██║╚█████╔╝██║██║░░██║██║░░██║  ╚█████╔╝██║░░██║██║░░██║██║░░██║██║░░░██║░░░╚█████╔╝
# ░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝  ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░╚═╝░░░░╚════╝░

@login_required(login_url='/login')
def vaciar_carrito(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)

    for item in carrito_items:
        item.delete()

    # Redirige de nuevo a la página del carrito (o a donde desees).
    return redirect('caja')  # Ajusta 'nombre_de_la_vista_del_carrito'.


# ███████╗██████╗░██╗████████╗░█████╗░██████╗░  ███╗░░░███╗░█████╗░███╗░░██╗████████╗░█████╗░  ██████╗░███████╗
# ██╔════╝██╔══██╗██║╚══██╔══╝██╔══██╗██╔══██╗  ████╗░████║██╔══██╗████╗░██║╚══██╔══╝██╔══██╗  ██╔══██╗██╔════╝
# █████╗░░██║░░██║██║░░░██║░░░███████║██████╔╝  ██╔████╔██║██║░░██║██╔██╗██║░░░██║░░░██║░░██║  ██║░░██║█████╗░░
# ██╔══╝░░██║░░██║██║░░░██║░░░██╔══██║██╔══██╗  ██║╚██╔╝██║██║░░██║██║╚████║░░░██║░░░██║░░██║  ██║░░██║██╔══╝░░
# ███████╗██████╔╝██║░░░██║░░░██║░░██║██║░░██║  ██║░╚═╝░██║╚█████╔╝██║░╚███║░░░██║░░░╚█████╔╝  ██████╔╝███████╗
# ╚══════╝╚═════╝░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝  ╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░░╚════╝░  ╚═════╝░╚══════╝

# ░█████╗░░█████╗░░░░░░██╗░█████╗░  ██╗░░░██╗  ██████╗░███████╗████████╗██╗██████╗░░█████╗░
# ██╔══██╗██╔══██╗░░░░░██║██╔══██╗  ╚██╗░██╔╝  ██╔══██╗██╔════╝╚══██╔══╝██║██╔══██╗██╔══██╗
# ██║░░╚═╝███████║░░░░░██║███████║  ░╚████╔╝░  ██████╔╝█████╗░░░░░██║░░░██║██████╔╝██║░░██║
# ██║░░██╗██╔══██║██╗░░██║██╔══██║  ░░╚██╔╝░░  ██╔══██╗██╔══╝░░░░░██║░░░██║██╔══██╗██║░░██║
# ╚█████╔╝██║░░██║╚█████╔╝██║░░██║  ░░░██║░░░  ██║░░██║███████╗░░░██║░░░██║██║░░██║╚█████╔╝
# ░╚════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝  ░░░╚═╝░░░  ╚═╝░░╚═╝╚══════╝░░░╚═╝░░░╚═╝╚═╝░░╚═╝░╚════╝░
@login_required(login_url='/login')
def editar_monto_caja_diaria(request):
    # Intenta recuperar el objeto CajaDiaria con ID 1 o crea uno nuevo si no existe
    caja_diaria, created = CajaDiaria.objects.get_or_create(id=1, defaults={'monto': 0.0, 'retiro': 0.0})

    if request.method == 'POST':
        # Obtén el valor actual del monto y el retiro antes de guardar
        monto_anterior = caja_diaria.monto
        retiro_anterior = caja_diaria.retiro
        

        # Verifica si se envió una operación de suma o resta
        operacion = request.POST.get('operacion', None)

        if operacion == 'sumar':
            
            monto_a_sumar = Decimal(request.POST.get('monto', 0.0))
            if monto_a_sumar != 0:
                abrir_caja_impresora()
            caja_diaria.monto += monto_a_sumar
            
        elif operacion == 'restar':
            
            monto_a_restar = Decimal(request.POST.get('monto', 0.0))
            if monto_a_restar <= caja_diaria.monto:
                if monto_a_restar != 0:
                    abrir_caja_impresora()
                caja_diaria.monto -= monto_a_restar
            else:
                # Muestra un mensaje de error si se intenta restar más de lo disponible
                messages.error(request, 'No puedes restar más de lo que tienes disponible en la caja.')


        if operacion == 'sumar_retiro':
            # Sumar al retiro existente
            retiro_a_sumar = Decimal(request.POST.get('retiro', 0.0))
            if retiro_a_sumar !=0:
                abrir_caja_impresora()
            caja_diaria.retiro += retiro_a_sumar
        elif operacion == 'restar_retiro':
            
            # Restar al retiro existente si es posible
            retiro_a_restar = Decimal(request.POST.get('retiro', 0.0))
            if retiro_a_restar <= caja_diaria.retiro:
                if retiro_a_restar != 0:
                    abrir_caja_impresora()
                caja_diaria.retiro -= retiro_a_restar
            else:
                messages.error(request, 'No puedes restar más de lo que tienes disponible en el retiro.')

        # Asegúrate de que el retiro nunca sea menor que cero
        if caja_diaria.retiro < 0:
            caja_diaria.retiro = 0


        caja_diaria.save()

        return redirect('editar_caja_diaria')  # Reemplaza 'nombre_de_la_vista' con el nombre de la vista a la que deseas redirigir después de la edición.

    else:
        form = CajaDiariaForm(instance=caja_diaria)

    return render(request, 'editar_caja_diaria.html', {'form': form})


# ██╗███╗░░██╗░██████╗░██████╗░███████╗░██████╗░█████╗░██████╗░  ░██████╗░░█████╗░░██████╗████████╗░█████╗░
# ██║████╗░██║██╔════╝░██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗  ██╔════╝░██╔══██╗██╔════╝╚══██╔══╝██╔══██╗
# ██║██╔██╗██║██║░░██╗░██████╔╝█████╗░░╚█████╗░███████║██████╔╝  ██║░░██╗░███████║╚█████╗░░░░██║░░░██║░░██║
# ██║██║╚████║██║░░╚██╗██╔══██╗██╔══╝░░░╚═══██╗██╔══██║██╔══██╗  ██║░░╚██╗██╔══██║░╚═══██╗░░░██║░░░██║░░██║
# ██║██║░╚███║╚██████╔╝██║░░██║███████╗██████╔╝██║░░██║██║░░██║  ╚██████╔╝██║░░██║██████╔╝░░░██║░░░╚█████╔╝
# ╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝  ░╚═════╝░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░░╚════╝░

@login_required(login_url='/login')
def ingresar_gasto(request):
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        return redirect('login')  # O redirige a otra página de acceso no autorizado

    if request.method == 'POST':
        form = GastoCajaForm(request.POST)
        if form.is_valid():
            # Realiza la autenticación adicional aquí
            clave_anulacion = request.POST.get('clave_anulacion', '')  # Obtener la clave ingresada en el formulari
            try:
                # Intenta buscar un usuario con la misma clave de anulación
                usuario_con_clave_anulacion = Usuario.objects.get(clave_anulacion=clave_anulacion)

                gasto = form.save(commit=False)  # No guardes inmediatamente en la base de datos
                gasto.usuario = usuario_con_clave_anulacion # Asigna el usuario autenticado al gasto
                gasto.save()  # Guarda el gasto en la base de datos
                messages.error(request, 'Gasto ingresado.')
                abrir_caja_impresora()
                return redirect('ingresar_gasto')  # Redirige a la lista de gastos después de guardar
        
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado para la clave de anulación proporcionada.')
    else:
        form = GastoCajaForm()

    return render(request, 'ingresar_gasto.html', {'form': form})

class ProductoListView(ListView):
    model = Producto  # Modelo a utilizar
    template_name = 'producto_list.html'  # Nombre de la plantilla HTML para mostrar la lista de productos
    context_object_name = 'productos'  # Nombre de la variable de contexto en la plantilla
    paginate_by = 10  # Cantidad de productos por página

    def get_queryset(self):
        query = self.request.GET.get('q')
        departamento_id = self.request.GET.get('departamento_id')  # Obtener el ID del departamento de la URL
        if query == "None":
            return Producto.objects.filter(departamento__isnull=True)
        if query:
            # Realizar la búsqueda por nombre, descripción, código de barras y departamento
            return Producto.objects.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(codigo_barras__icontains=query) |
                Q(departamento__nombre__icontains=query)  # Reemplaza 'nombre' por el campo correcto de Departamento
            )

        elif departamento_id:
            # Filtrar por departamento si se proporciona el ID del departamento en la URL
            return Producto.objects.filter(departamento_id=departamento_id)
        else:
            return Producto.objects.all()
        

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'codigo_barras', 'gramaje', 'foto', 'descripcion', 'departamento', 'marca', 'tipo_gramaje', 'tipo_venta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control onlyinput'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control onlyinput'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control onlyinput'}),
            'gramaje': forms.NumberInput(attrs={'class': 'form-control onlyinput'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control onlyinput'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control onlyinput'}),
            'departamento': forms.Select(attrs={'class': 'form-control onlyinput'}),
            'marca': forms.Select(attrs={'class': 'form-control onlyinput'}),
            'tipo_gramaje': forms.Select(attrs={'class': 'form-control onlyinput'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-control onlyinput'}),
        }

class ProductoEditarView(UpdateView):
    model = Producto
    template_name = 'producto_editar.html'
    form_class = ProductoForm
    success_url = '/productos/'

def imprimir_ultima_id():
    try:
        # Obtener la última ID desde tu modelo
        ultima_id = Venta.objects.latest('id')

        # Convertir la ID a una cadena (si es necesario)
        ultima_id_str = str(ultima_id.id)


        venta = Venta.objects.get(id=ultima_id_str)

        contest = generar_comandos_de_impresion(venta)

        imprimir_en_xprinter(contest)
    except:
        pass

def obtener_ultima_venta():
    try:
        # Obtener la última ID desde tu modelo
        ultima_id = Venta.objects.latest('id')

        # Convertir la ID a una cadena (si es necesario)
        ultima_id_str = str(ultima_id.id)


        venta = Venta.objects.get(id=ultima_id_str)
        
        return venta
    except:
        pass

def impresora_no_conectada(request):
    return render(request, 'no_impresora.html')

def impresora_si_conectada(request):
    return render(request, 'si_impresora.html')

@login_required
def cambiar_usuario(request, usuario_id):
    usuario = Usuario.objects.get(pk=usuario_id)

    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            # Verificar si el nuevo valor de permisos es "admin"
            nuevo_permiso = form.cleaned_data['permisos']
            if nuevo_permiso == 'admin':
                # Si el nuevo permiso es "admin", cambiar a superusuario
                user_instance = form.save(commit=False)
                user_instance.is_superuser = True
                user_instance.is_staff = True
                user_instance.save()
            else:
                # Si el nuevo permiso no es "admin", asegúrate de quitar el estado de superusuario
                user_instance = form.save(commit=False)
                user_instance.is_superuser = False
                user_instance.is_staff = False
                user_instance.save()

            return redirect('lista_usuarios')
    else:
        form = UsuarioChangeForm(instance=usuario)

    return render(request, 'editar_usuario.html', {'form': form})

@login_required
def cambiar_clave_anulacion(request, usuario_id):
    usuario = Usuario.objects.get(pk=usuario_id)

    if request.method == 'POST':
        form = CambiarClaveAnulacionForm(request.POST, instance=usuario)
        if form.is_valid():
            clave_anulacion = form.cleaned_data['nueva_clave_anulacion']

            # Verificar si la nueva clave de anulación ya está en uso por otro usuario
            if Usuario.objects.exclude(pk=usuario_id).filter(clave_anulacion=clave_anulacion).exists():
                messages.error(request, 'La nueva clave de anulación ya está en uso por otro usuario.')
            else:
                usuario.clave_anulacion = clave_anulacion
                usuario.save()
                messages.success(request, 'La nueva clave de anulación se guardo.')
                return redirect('lista_usuarios')
    else:
        form = CambiarClaveAnulacionForm(instance=usuario)

    return render(request, 'editar_clave_anulacion.html', {'form': form})
