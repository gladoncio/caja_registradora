#!/bin/bash

# Cambia al directorio de tu proyecto Django
cd /home/bravito/Documentos/GitHub/caja_registradora

# Ejecuta el servidor Django
python3 manage.py runserver 192.168.0.25:8000&

# Espera un momento para que el servidor se inicie
sleep 5

# Abre el navegador en la ruta de tu aplicación
firefox http://192.168.0.25:8000/

