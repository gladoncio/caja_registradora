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
import io
from .views import generar_comandos_de_impresion


USB = "/dev/usb/lp0"

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
    print(content)

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
    # Comando en formato binario para abrir la gaveta
    open_drawer_command = b'\x1B\x70\x00\x50\x50'

    # Abre el archivo correspondiente al dispositivo USB
    with open(USB, 'wb') as usb_device:
        usb_device.write(open_drawer_command)

    return "La gaveta se abrió"



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