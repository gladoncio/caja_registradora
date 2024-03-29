import subprocess
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from barcode import generate
import sys
from unidecode import unidecode
from django.http import HttpResponse
import random
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image
from django.utils.formats import date_format
import io
import os
from .middleware import verificar_impresora_conectada


USB = verificar_impresora_conectada()


# ░██████╗░███████╗███╗░░██╗███████╗██████╗░░█████╗░██████╗░  ███████╗██╗░░░░░
# ██╔════╝░██╔════╝████╗░██║██╔════╝██╔══██╗██╔══██╗██╔══██╗  ██╔════╝██║░░░░░
# ██║░░██╗░█████╗░░██╔██╗██║█████╗░░██████╔╝███████║██████╔╝  █████╗░░██║░░░░░
# ██║░░╚██╗██╔══╝░░██║╚████║██╔══╝░░██╔══██╗██╔══██║██╔══██╗  ██╔══╝░░██║░░░░░
# ╚██████╔╝███████╗██║░╚███║███████╗██║░░██║██║░░██║██║░░██║  ███████╗███████╗
# ░╚═════╝░╚══════╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝  ╚══════╝╚══════╝

# ░█████╗░░█████╗░███╗░░██╗████████╗███████╗██╗░░██╗████████╗░█████╗░  ██████╗░███████╗  ██╗░░░░░░█████╗░
# ██╔══██╗██╔══██╗████╗░██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗  ██╔══██╗██╔════╝  ██║░░░░░██╔══██╗
# ██║░░╚═╝██║░░██║██╔██╗██║░░░██║░░░█████╗░░░╚███╔╝░░░░██║░░░██║░░██║  ██║░░██║█████╗░░  ██║░░░░░███████║
# ██║░░██╗██║░░██║██║╚████║░░░██║░░░██╔══╝░░░██╔██╗░░░░██║░░░██║░░██║  ██║░░██║██╔══╝░░  ██║░░░░░██╔══██║
# ╚█████╔╝╚█████╔╝██║░╚███║░░░██║░░░███████╗██╔╝╚██╗░░░██║░░░╚█████╔╝  ██████╔╝███████╗  ███████╗██║░░██║
# ░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░╚════╝░  ╚═════╝░╚══════╝  ╚══════╝╚═╝░░╚═╝

# ██╗░░░██╗███████╗███╗░░██╗████████╗░█████╗░
# ██║░░░██║██╔════╝████╗░██║╚══██╔══╝██╔══██╗
# ╚██╗░██╔╝█████╗░░██╔██╗██║░░░██║░░░███████║
# ░╚████╔╝░██╔══╝░░██║╚████║░░░██║░░░██╔══██║
# ░░╚██╔╝░░███████╗██║░╚███║░░░██║░░░██║░░██║
# ░░░╚═╝░░░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝

def generar_comandos_de_impresion(venta):
    config = Configuracion.objects.get(id=1)
    decimales = config.decimales

    # Inicializa una cadena vacía para almacenar los comandos de impresión
    content = ""
    content += "--------------------------\n"

    # Encabezado de la boleta (puedes personalizarlo según tus necesidades)
    content += "Boleta de Venta\n"
    content += f"Fecha: {timezone.localtime(venta.fecha_hora).strftime('%Y-%m-%d %H:%M:%S')} \n"

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
        gramaje = venta_producto.gramaje
        precio_unitario = round(venta_producto.subtotal, decimales)  # Formatea el precio unitario
        # Agrega los detalles de cada producto a la boleta
        content += f"Producto: {producto.nombre}\n"
        if cantidad != 0:
            content += f"Cantidad: {cantidad}\n"
        else:
            content += f"Cantidad: {gramaje} gramos\n"
        content += f"Subtotal: {precio_unitario}\n"
        content += "--------------------------\n"

    # Total de la venta
    total_venta = round(venta.total, decimales)  
    vuelto = round(venta.vuelto, decimales)# Formatea el total de la venta
    content += f"vuelto: {vuelto}\n"
    content += f"Total: {total_venta}\n"
    content += "--------------------------\n"
    return content



def generar_y_imprimir_codigo_ean13(request):
    try:
        # Genera un número aleatorio de 12 dígitos para el código de barras EAN-13
        codigo_de_barras = ''.join([str(random.randint(0, 9)) for _ in range(12)])

        # Crea el objeto EAN-13
        ean = EAN13(codigo_de_barras, writer=ImageWriter())

        # Genera el código de barras como una imagen PNG
        barcode_image = ean.render()

        # Guarda la imagen en un archivo temporal
        tmp_image_path = "media/barcode.png"
        barcode_image.save(tmp_image_path, 'PNG')

        # Imprimir la imagen usando lpr
        command = f'lpr -o raw {tmp_image_path} -P {USB}'
        subprocess.call(command, shell=True)

        # Devuelve la imagen como respuesta HTTP (opcional)
        response = HttpResponse(content_type='image/png')
        barcode_image.save(response, 'PNG')

        return response

    except Exception as e:
        return HttpResponse(f"Error al generar e imprimir el código de barras: {str(e)}", status=500)


def imprimir_en_xprinter(content):
    config = Configuracion.objects.get(id=1)

    # Elimina los acentos del contenido
    content_normalized = unidecode(content)

    # Codifica el contenido en UTF-8
    content_encoded = content_normalized.encode('utf-8')

    
    with open(USB, 'wb') as printer_file:
        printer_file.write(content_encoded)

    return "Impresión exitosa"


def imprimir(request):
    try:
        data_to_print = "Imprimiendo desde Python usando redirección de shell >> /dev/usb/lp0"

        command = f'echo "{data_to_print}" >> {USB}'

        # Ejecutar el comando en el shell
        subprocess.call(command, shell=True)

        return HttpResponse("Impresión exitosa")  # Esto devuelve una respuesta HTTP con un mensaje de éxito.
    except Exception as e:
        return HttpResponse(f"Error al imprimir: {str(e)}", status=500)  # Esto devuelve una respuesta HTTP con un mensaje de error y un estado 500 (Error interno del servidor).

def abrir_caja_impresora():
    try:
        # Comando en formato binario para abrir la gaveta
        open_drawer_command = b'\x1B\x70\x00\x50\x50'

        # Abre el archivo correspondiente al dispositivo USB
        with open(USB, 'wb') as usb_device:
            usb_device.write(open_drawer_command)

        return True
    except:
        return False



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

