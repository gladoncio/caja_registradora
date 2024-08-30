from django.shortcuts import redirect
import os

impresora_validar = "si"

def verificar_impresora_conectada():
    # Directorio donde se encuentran los dispositivos USB
    usb_directory = "/dev/usb/"

    try:
        # Listar los archivos en el directorio USB
        usb_devices = os.listdir(usb_directory)

        # Filtrar los archivos que comienzan con 'lp'
        lp_devices = [device for device in usb_devices if device.startswith('lp')]

        # Seleccionar el primer dispositivo 'lp' disponible (puedes ajustar esto según tus necesidades)
        if lp_devices:
            USB = os.path.join(usb_directory, lp_devices[0])
            print(f"Dispositivo USB seleccionado: {USB}")
            # Puedes hacer más acciones aquí si hay una impresora conectada
            return USB
        else:
            # En caso de que no se encuentre ningún dispositivo 'lp'
            print("Ninguna impresora conectada")
            return None

    except FileNotFoundError:
        # En caso de que el directorio no exista
        print(f"Directorio USB no encontrado: {usb_directory}")
        return None


class ImpresoraMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Realiza la verificación de la impresora en cada solicitud
        USB = verificar_impresora_conectada()

        if not USB and not request.path.startswith('/impresora-no-conectada/'):
            if impresora_validar!="no":
            # Si no hay impresora y no estás ya en la página de impresora no conectada, redirige
                return redirect('impresora_no_conectada')

        response = self.get_response(request)
        return response