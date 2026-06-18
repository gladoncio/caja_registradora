from django.shortcuts import redirect
from .models import Configuracion
import os
import socket
from time import time

_printer_cache = {'result': None, 'time': 0}
impresora_validar = "no"


def verificar_impresora_conectada():
    now = time()
    if now - _printer_cache['time'] < 30:
        return _printer_cache['result']

    try:
        config = Configuracion.objects.get(id=1)
    except Configuracion.DoesNotExist:
        return None

    result = None
    if config.tipo_impresora == 'ip':
        ip = config.ip_impresora or '192.168.100.30'
        puerto = config.puerto_impresora or 9100
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, puerto))
            sock.close()
            result = f"ip:{ip}:{puerto}"
        except:
            pass
    else:
        usb_directory = "/dev/usb/"
        try:
            usb_devices = os.listdir(usb_directory)
            lp_devices = [device for device in usb_devices if device.startswith('lp')]
            if lp_devices:
                result = os.path.join(usb_directory, lp_devices[0])
        except FileNotFoundError:
            pass

    _printer_cache['result'] = result
    _printer_cache['time'] = now
    return result


class ImpresoraMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        USB = verificar_impresora_conectada()

        if not USB and not request.path.startswith('/impresora-no-conectada/'):
            if impresora_validar != "no":
                return redirect('impresora_no_conectada')

        response = self.get_response(request)
        return response
