#!/bin/sh
# Obtener la versión desde el archivo
VERSION=$(cat version.txt)

# Actualizar el código fuente desde el repositorio remoto usando la versión o etiqueta específica
git fetch origin --tags
git checkout $VERSION

