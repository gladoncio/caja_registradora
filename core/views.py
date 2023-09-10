from multiprocessing import context
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
from django.db.models import Sum
from escpos.printer import Usb
from usb.core import USBError
from django.http import HttpResponse
import requests
import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from .funciones import *
import barcode
from barcode import generate
from django.conf import settings  # Agrega esta importación
from io import BytesIO
from django.urls import reverse


def abrir_caja_impresora():
    try:
        # Abre una conexión con la impresora a través de USB (sustituye los valores con los adecuados)
        printer = Usb(0x1fc9, 0x2016)

        # Envía el comando para abrir la caja
        printer.cashdraw(2)  # El número puede variar según la impresora

        # Cierra la conexión con la impresora
        printer.close()

        return True  # Éxito al abrir la caja
    except Exception as e:
        return False  # Error al abrir la caja

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
def generar_venta(request, parametro1, parametro2, parametro3):
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
                VentaProducto.objects.create(venta=nueva_venta, producto=item.producto, cantidad=item.cantidad, gramaje=item.gramaje, subtotal=subtotal)
            nueva_venta.total = total_venta
            nueva_venta.save()
            
            # Vaciar el carrito del usuario
            carrito_items.delete()
            parametro3 = float(parametro3)
            total_venta = float(nueva_venta.total)
            monto_efectivo = total_venta - parametro3
            print(monto_efectivo)
            
            if parametro1 == "venta_con_restante":
                FormaPago.objects.create(venta=nueva_venta, tipo_pago=parametro2, monto=parametro3)
                if monto_efectivo > 0:
                    FormaPago.objects.create(venta=nueva_venta, tipo_pago="efectivo", monto=monto_efectivo)
            elif parametro1 == "venta_sin_restante":
                FormaPago.objects.create(venta=nueva_venta, tipo_pago=parametro2, monto=total_venta)
            
            # Verifica si el método de pago es efectivo y llama a la función abrir_caja_impresora
            if parametro1 == "venta_con_restante" or parametro1 == "efectivo":
                if abrir_caja_impresora():
                    messages.success(request, 'Caja abierta exitosamente.')
                else:
                    messages.error(request, 'Error al abrir la caja. Inténtalo de nuevo.')
            
            # Llama a la función para imprimir la boleta
            content = generar_comandos_de_impresion(nueva_venta)
            imprimir_en_xprinter(content)
            
            return redirect('caja')  # Cambiar por la página deseada
        else:
            # Manejar el caso donde el carrito del usuario está vacío
            pass
    except Exception as e:
        # Manejar excepciones u otros errores
        pass
    
    # Redireccionar a la página del carrito si ocurre algún error
    return redirect('caja')  # Cambiar por la página del carrito

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
        fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()

        # Filtra las ventas por la fecha seleccionada
        ventas = ventas.filter(fecha_hora__date=fecha)

    if hora_inicio and hora_fin:
        # Formatea las horas de inicio y fin en objetos de tiempo
        hora_inicio = datetime.datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin = datetime.datetime.strptime(hora_fin, "%H:%M").time()

        # Filtra las ventas por el rango de horas
        ventas = ventas.filter(fecha_hora__time__range=(hora_inicio, hora_fin))

    return render(request, 'lista_ventas.html', {'ventas': ventas})




def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    productos_vendidos = VentaProducto.objects.filter(venta=venta)
    formas_pago = FormaPago.objects.filter(venta=venta)
    return render(request, 'detalle_venta.html', {'venta': venta, 'productos_vendidos': productos_vendidos, 'formas_pago': formas_pago})




def informe_general(request):
    caja_diaria, created = CajaDiaria.objects.get_or_create(id=1, defaults={'monto': 0.0, 'retiro': 0.0})
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

    return render(request, 'informe_general.html', {
        'total_ventas_despues_ultima_fecha': total_ventas_despues_ultima_fecha,
        'monto_efectivo': monto_efectivo,
        'monto_credito': monto_credito,
        'monto_debito': monto_debito,
        'monto_transferencia': monto_transferencia,
        'monto_retiro' : caja_diaria.retiro,
        'monto_caja' : caja_diaria.monto,
    })



def cerrar_caja(request):
    caja_diaria, created = CajaDiaria.objects.get_or_create(id=1, defaults={'monto': 0.0, 'retiro': 0.0})
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


    caja_diaria_nueva = monto_efectivo + caja_diaria.monto - caja_diaria.retiro

    caja_diaria.monto = caja_diaria_nueva
    caja_diaria.retiro = 0.0
    caja_diaria.save()

    # Redirigir a la página de informe general
    return redirect('informe_general')


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
            # Sumar al monto existente
            monto_a_sumar = Decimal(request.POST.get('monto', 0))
            caja_diaria.monto += monto_a_sumar
        elif operacion == 'restar':
            # Restar al monto existente si es posible
            monto_a_restar = Decimal(request.POST.get('monto', 0))
            if monto_a_restar <= caja_diaria.monto:
                caja_diaria.monto -= monto_a_restar
            else:
                # Muestra un mensaje de error si se intenta restar más de lo disponible
                messages.error(request, 'No puedes restar más de lo que tienes disponible en la caja.')


        if operacion == 'sumar_retiro':
            # Sumar al retiro existente
            retiro_a_sumar = Decimal(request.POST.get('retiro', 0))
            caja_diaria.retiro += retiro_a_sumar
        elif operacion == 'restar_retiro':
            # Restar al retiro existente si es posible
            retiro_a_restar = Decimal(request.POST.get('retiro', 0))
            if retiro_a_restar <= caja_diaria.retiro:
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

def cuadrar(request):
    caja_diaria, created = CajaDiaria.objects.get_or_create(id=1, defaults={'monto': 0.0, 'retiro': 0.0})
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
            
            total_efectivo = (monedas_10 * 10) + (monedas_50 * 50) + (monedas_100 * 100) + (monedas_500 * 500) + (billetes_1000 * 1000) + (billetes_2000 * 2000) + (billetes_5000 * 5000) + (billetes_10000 * 10000) + (billetes_20000 * 20000)

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

            monto_que_deberia_dar = monto_efectivo + caja_diaria.monto - caja_diaria.retiro
            
            cuadre = Cuadre.objects.create(
            usuario=request.user,  # Supongo que quieres asociar al usuario actual
            fecha_ingreso=timezone.now(),  # Utiliza timezone.now() para obtener la fecha y hora actual
            # Otra información que quieras guardar en el modelo Cuadre
            )

            
            
            context = {
                'total' : total_ventas_despues_ultima_fecha,
                'caja_diaria': caja_diaria.monto,
                'retiro' : caja_diaria.retiro,
                'monto_efectivo': monto_efectivo,
                'monto_credito': monto_credito,
                'monto_debito': monto_debito,
                'monto_transferencia': monto_transferencia,
                'monto_que_deberia_dar': monto_que_deberia_dar,
                'total_en_caja':  total_efectivo
            }

            return render(request, 'resultado_cuadre.html', context)
    else:
        form = BilletesMonedasForm()

    return render(request, 'cerrar_caja.html', {'form': form})

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

    
    



def download_latest_version(tag_name):
    # URL del archivo ZIP de la última versión en GitHub
    url = f"https://github.com/gladoncio/caja_registradora/archive/{tag_name}.zip"

    # Ruta local donde se almacenará el archivo ZIP descargado
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    local_file_path = os.path.join(current_file_directory, f"latest_version.zip")

    # Realizar la descarga
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"No se pudo descargar la última versión. Código de estado: {response.status_code}")

    # Descomprimir el archivo ZIP
    extracted_directory = os.path.join(current_file_directory, f"latest_version_extracted")
    with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_directory)

    # Eliminar el archivo ZIP descargado
    os.remove(local_file_path)

    # Regresar la ruta local donde se descomprimió la última versión
    return extracted_directory

def update_project(new_version_directory, project_directory):
    for root, _, files in os.walk(new_version_directory):
        for file in files:
            source_file = os.path.join(root, file)
            relative_path = os.path.relpath(source_file, new_version_directory)
            destination_file = os.path.join(project_directory, relative_path)

            # Copiar el archivo siempre, incluso si ya existe
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)
            shutil.copy2(source_file, destination_file)

def update(request):
    # Directorio donde está ubicado tu proyecto Django (la carpeta "caja_registradora")
    project_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Descargar la última versión desde GitHub (puedes usar tu función check_github_version)
    latest_version = check_github_version()

    fecha = get_github_latest_release_date()

    fecha_actualizacion = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%SZ")

    nueva_actualizacion, created = ActualizacionModel.objects.get_or_create(id=1, fecha_actualizacion=fecha_actualizacion)

    nueva_actualizacion.save()

    new_version_directory = download_latest_version(latest_version)

    # Actualizar el proyecto
    update_project(new_version_directory, project_directory)

    # Reiniciar la aplicación (puedes adaptarlo a tu servidor web)

    return render(request, 'update.html')


def abrir_caja(request):
    configuracion = Configuracion.objects.first()
    if request.method == 'POST':
        form = ContraseñaForm(request.POST)
        if form.is_valid():
            # Verifica si la contraseña es correcta
            contraseña = form.cleaned_data['contraseña']
            if contraseña == configuracion.clave_anulacion:  # Reemplaza 'tu_contraseña_correcta' con la contraseña correcta
                try:
                    # Abre una conexión con la impresora a través de USB (sustituye los valores con los adecuados)
                    printer = Usb(0x1fc9, 0x2016)

                    # Envía el comando para abrir la caja
                    printer.cashdraw(2)  # El número puede variar según la impresora

                    # Cierra la conexión con la impresora
                    printer.close()

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

def imprimir(request):
    try:
        printer = Usb(0x1fc9, 0x2016)

        # Imprimir un texto de ejemplo
        text_to_print = "¡Hola, mundo desde Python con Xprinter XP-80C!"
        printer.text(text_to_print)
        printer.cut()

        # Cerrar la conexión con la impresora
        printer.close()


        return HttpResponse("Impresión exitosa")  # Esto devuelve una respuesta HTTP con un mensaje de éxito.
    except Exception as e:
        return HttpResponse(f"Error al imprimir: {str(e)}", status=500)  # Esto devuelve una respuesta HTTP con un mensaje de error y un estado 500 (Error interno del servidor).
    
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


def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')  # Mensaje de éxito
            return redirect('crear_usuario')  # Redirige a la página de éxito después de crear el usuario
        else:
            messages.error(request, 'Ha ocurrido un error. Por favor, revise el formulario.')  # Mensaje de error
    else:
        form = UsuarioCreationForm()

    return render(request, 'crear_usuario.html', {'form': form})


def imprimir_boleta(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)

    # Genera el contenido de la boleta en formato de comandos de impresión para Xprinter XP-80C
    content = generar_comandos_de_impresion(venta)

    # Envía los comandos de impresión a la impresora USB
    imprimir_en_xprinter(content)

    # Devuelve una respuesta vacía o un mensaje de éxito
    return HttpResponse("Boleta impresa exitosamente")

def generar_comandos_de_impresion(venta):
    # Inicializa una cadena vacía para almacenar los comandos de impresión
    content = ""
    content += "--------------------------\n"

    # Encabezado de la boleta (puedes personalizarlo según tus necesidades)
    content += "Boleta de Venta\n"
    content += f"Fecha: {venta.fecha_hora}\n"
    
    # Agregar el método de pago de esta venta
    formas_pago = venta.formapago_set.all()
    if formas_pago.exists():
        metodos_pago = ", ".join([forma.tipo_pago for forma in formas_pago])
        content += f"Método(s) de Pago: {metodos_pago}\n"
    
    content += "--------------------------\n"

    # Detalles de los productos vendidos
    for venta_producto in venta.ventaproducto_set.all():
        producto = venta_producto.producto
        cantidad = venta_producto.cantidad
        precio_unitario = producto.precio

        # Agrega los detalles de cada producto a la boleta
        content += f"Producto: {producto.nombre}\n"
        content += f"Cantidad: {cantidad}\n"
        content += f"Precio Unitario: {precio_unitario}\n"
        content += "--------------------------\n"

    # Total de la venta
    total_venta = venta.total
    content += f"Total: {total_venta}\n"
    content += "--------------------------\n"
    return content


def imprimir_en_xprinter(content):
    # Abre una conexión con la impresora a través de USB (sustituye los valores con los adecuados)
    printer = Usb(0x1fc9, 0x2016)

    # Envía el contenido de la boleta como comandos de impresión
    printer.text(content)

    # Realiza un corte de papel (puede variar según la impresora)
    #printer.cut()

    # Cierra la conexión con la impresora
    printer.close()

def seleccionar_metodo_pago(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in carrito_items)
    metodos_pago = ["Efectivo", "Transferencia", "Débito", "Crédito"]
    context = {'metodos_pago': metodos_pago, 'total' : total}
    return render(request, 'seleccionar_pago.html', context)

def procesar_pago(request):
    if request.method == 'POST':
        metodo_pago_seleccionado = request.POST.get('metodoPago')
        
        if metodo_pago_seleccionado == 'Efectivo':
            # Redirige a la vista para ingresar el monto en efectivo
            return redirect('ingresar_monto_efectivo')
        elif metodo_pago_seleccionado == 'Transferencia':
            # Redirige a la vista generar_venta con los parámetros adecuados para Transferencia
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'Transferencia', '0'])
            return redirect(url_generar_venta)
        elif metodo_pago_seleccionado == 'Débito':
            # Redirige a la vista generar_venta con los parámetros adecuados para Débito
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'Débito', '0'])
            return redirect(url_generar_venta)
        elif metodo_pago_seleccionado == 'Crédito':
            # Redirige a la vista generar_venta con los parámetros adecuados para Crédito
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'Crédito', '0'])
            return redirect(url_generar_venta)
    
    # Redirige a una vista predeterminada en caso de error o si no se seleccionó un método de pago válido
    return redirect('caja')  # Cambiar por la página deseada


def ingresar_monto_efectivo(request):
    carrito_items = CarritoItem.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in carrito_items)

    if request.method == 'POST':
        # Obtener el monto ingresado por el usuario
        monto_efectivo = float(request.POST.get('monto_efectivo', '0'))
        if monto_efectivo >= total:
            url_generar_venta = reverse('generar_venta', args=['venta_sin_restante', 'efectivo', monto_efectivo])
            return redirect(url_generar_venta)
        else:
            # Redirigir a la vista seleccionar_metodo_pago_resto
            url_seleccionar_metodo_pago_resto = reverse('seleccionar_metodo_pago_resto', args=[total, monto_efectivo])
            return redirect(url_seleccionar_metodo_pago_resto)

    context = {'total': total}
    return render(request, 'ingresar_monto_efectivo.html', context)


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
        
        # Redirige a la vista para procesar el pago con los parámetros necesarios
        return redirect('procesar_pago_restante', metodo_pago=metodo_pago_seleccionado, restante=restante)

    # De lo contrario, renderiza la página de selección de método de pago
    return render(request, 'seleccionar_metodo_pago_resto.html', context)


def procesar_pago_restante(request, metodo_pago, restante):
    url_generar_venta = reverse('generar_venta', args=['venta_con_restante', metodo_pago, restante])
    return redirect(url_generar_venta)
