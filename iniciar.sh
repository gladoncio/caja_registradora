#!/bin/bash

# Cambia al directorio de tu proyecto Django
cd /home/bravito/Documentos/GitHub/caja_registradora

# Ejecuta el servidor Django
python3 manage.py runserver &

# Espera un momento para que el servidor se inicie
sleep 5

# Abre el navegador en la ruta de tu aplicación
firefox http://localhost:8000/

