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
import socket


def _detectar_usb():
    usb_directory = "/dev/usb/"
    try:
        usb_devices = os.listdir(usb_directory)
        lp_devices = [device for device in usb_devices if device.startswith('lp')]
        if lp_devices:
            return os.path.join(usb_directory, lp_devices[0])
    except FileNotFoundError:
        pass
    return None


def _enviar_a_impresora(data):
    config = Configuracion.objects.get(id=1)
    if config.tipo_impresora == 'ip':
        ip = config.ip_impresora or '192.168.100.30'
        puerto = config.puerto_impresora or 9100
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, puerto))
        sock.send(data)
        sock.close()
    else:
        usb_path = _detectar_usb()
        if not usb_path:
            raise Exception("No se encontro impresora USB")
        with open(usb_path, 'wb') as f:
            f.write(data)
    return True


def generar_comandos_de_impresion(venta):
    config = Configuracion.objects.get(id=1)
    decimales = config.decimales

    content = ""
    content += "--------------------------\n"
    content += "Boleta de Venta\n"
    content += f"Fecha: {timezone.localtime(venta.fecha_hora).strftime('%Y-%m-%d %H:%M:%S')} \n"

    formas_pago = venta.formapago_set.all()
    if formas_pago.exists():
        metodos_pago = ", ".join([forma.tipo_pago for forma in formas_pago])
        content += f"Metodo(s) de Pago: {metodos_pago}\n"

    content += "--------------------------\n"

    for venta_producto in venta.ventaproducto_set.all():
        producto = venta_producto.producto
        cantidad = venta_producto.cantidad
        gramaje = venta_producto.gramaje
        precio_unitario = round(venta_producto.subtotal, decimales)
        content += f"Producto: {producto.nombre}\n"
        if cantidad != 0:
            content += f"Cantidad: {cantidad}\n"
        else:
            content += f"Cantidad: {gramaje} gramos\n"
        content += f"Subtotal: {precio_unitario}\n"
        content += "--------------------------\n"

    total_venta = round(venta.total, decimales)
    vuelto = round(venta.vuelto, decimales)
    content += f"vuelto: {vuelto}\n"
    content += f"Total: {total_venta}\n"
    content += "--------------------------\n"
    return content


def generar_y_imprimir_codigo_ean13(request):
    try:
        codigo_de_barras = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        ean = EAN13(codigo_de_barras, writer=ImageWriter())
        barcode_image = ean.render()
        tmp_image_path = "media/barcode.png"
        barcode_image.save(tmp_image_path, 'PNG')

        config = Configuracion.objects.get(id=1)
        if config.tipo_impresora == 'ip':
            with open(tmp_image_path, 'rb') as f:
                img_data = f.read()
            _enviar_a_impresora(img_data)
        else:
            usb_path = _detectar_usb()
            if usb_path:
                command = f'lpr -o raw {tmp_image_path} -P {usb_path}'
                subprocess.call(command, shell=True)

        response = HttpResponse(content_type='image/png')
        barcode_image.save(response, 'PNG')
        return response
    except Exception as e:
        return HttpResponse(f"Error al generar e imprimir el codigo de barras: {str(e)}", status=500)


def imprimir_en_xprinter(content):
    config = Configuracion.objects.get(id=1)
    content_normalized = unidecode(content)
    content_encoded = content_normalized.encode('utf-8')

    if config.tipo_impresora == 'ip':
        _enviar_a_impresora(content_encoded)
    else:
        usb_path = _detectar_usb()
        if not usb_path:
            raise Exception("No se encontro impresora USB")
        with open(usb_path, 'wb') as printer_file:
            printer_file.write(content_encoded)

    return "Impresion exitosa"


def imprimir(request):
    try:
        data_to_print = "Test de impresion desde Caja Registradora\n"
        config = Configuracion.objects.get(id=1)

        if config.tipo_impresora == 'ip':
            _enviar_a_impresora(data_to_print.encode('utf-8'))
            return HttpResponse("Impresion exitosa")
        else:
            usb_path = _detectar_usb()
            if not usb_path:
                return HttpResponse("No se encontro impresora USB", status=500)
            command = f'echo "{data_to_print}" >> {usb_path}'
            subprocess.call(command, shell=True)
            return HttpResponse("Impresion exitosa")
    except Exception as e:
        return HttpResponse(f"Error al imprimir: {str(e)}", status=500)


def abrir_caja_impresora():
    try:
        open_drawer_command = b'\x1B\x70\x00\x50\x50'
        _enviar_a_impresora(open_drawer_command)
        return True
    except:
        return False


def imprimir_ultima_id():
    try:
        ultima_id = Venta.objects.latest('id')
        ultima_id_str = str(ultima_id.id)
        venta = Venta.objects.get(id=ultima_id_str)
        contest = generar_comandos_de_impresion(venta)
        imprimir_en_xprinter(contest)
    except:
        pass


def probar_impresora(request):
    try:
        config = Configuracion.objects.get(id=1)
        content = "==============================\n"
        content += "     TEST DE IMPRESION\n"
        content += "==============================\n"
        content += "Fecha: 2025-06-15 12:00\n"
        content += "------------------------------\n"
        content += "Producto       Cant   Total\n"
        content += "Pan            2      $1.000\n"
        content += "Leche          1      $1.200\n"
        content += "------------------------------\n"
        content += "Total: $2.200\n"
        content += "Gracias por su compra!\n"
        content += "\n\n"

        content_normalized = unidecode(content)
        content_encoded = content_normalized.encode('utf-8')

        if config.tipo_impresora == 'ip':
            ip = config.ip_impresora or '192.168.100.30'
            puerto = config.puerto_impresora or 9100
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, puerto))
            sock.send(b'\x1b\x40')
            sock.send(b'\x1b\x61\x01')
            sock.send(content_encoded)
            sock.send(b'\x1b\x69')
            sock.close()
        else:
            usb_path = _detectar_usb()
            if not usb_path:
                return HttpResponse("No se encontro impresora USB", status=500)
            with open(usb_path, 'wb') as f:
                f.write(b'\x1b\x40')
                f.write(content_encoded)
                f.write(b'\x1b\x69')

        return HttpResponse("Test de impresion enviado exitosamente")
    except Exception as e:
        return HttpResponse(f"Error en test de impresion: {str(e)}", status=500)
