#!/bin/sh

# Detener el servidor de Django si está en ejecución
pkill -f "python app/manage.py runserver"

# Obtener la versión desde el archivo
VERSION=$(cat version.txt)
# Actualizar el código fuente desde el repositorio remoto usando la versión o etiqueta específica
git fetch origin --tags
git checkout $VERSION

# Aplicar migraciones de la base de datos
python app/manage.py makemigrations
python app/manage.py migrate

# Reiniciar el servidor de Django
python app/manage.py runserver 0.0.0.0:8000 &
