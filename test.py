import subprocess
import barcode
from barcode.writer import ImageWriter

# Crear un código de barras (en este caso, EAN-13)
data = '123456789012'
ean = barcode.get_barcode_class('ean13')
code = ean(data, writer=ImageWriter(), add_checksum=False)

# Guardar el código de barras como una imagen
filename = 'barcode'
fullname = code.save(filename)

# Imprimir la imagen en la impresora
printer_path = '/dev/usb/lp0'
command = f'lpr -o fit-to-page -o media=A4 {fullname} -P {printer_path}'

# Ejecutar el comando en el shell
subprocess.call(command, shell=True)