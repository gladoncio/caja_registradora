from django.shortcuts import redirect
from .models import Configuracion
import os
import socket

impresora_validar = "no"


def verificar_impresora_conectada():
    try:
        config = Configuracion.objects.get(id=1)
    except Configuracion.DoesNotExist:
        return None

    if config.tipo_impresora == 'ip':
        ip = config.ip_impresora or '192.168.100.30'
        puerto = config.puerto_impresora or 9100
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip, puerto))
            sock.close()
            return f"ip:{ip}:{puerto}"
        except:
            return None
    else:
        usb_directory = "/dev/usb/"
        try:
            usb_devices = os.listdir(usb_directory)
            lp_devices = [device for device in usb_devices if device.startswith('lp')]
            if lp_devices:
                return os.path.join(usb_directory, lp_devices[0])
        except FileNotFoundError:
            pass
        return None


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
