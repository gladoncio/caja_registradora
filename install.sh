#!/bin/bash

# Obtener la ruta del directorio actual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Actualizar los paquetes del sistema
sudo apt update
sudo apt upgrade -y

# Instalar Docker
sudo apt install -y docker.io

# Iniciar y habilitar el servicio Docker
sudo systemctl start docker
sudo systemctl enable docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar la instalación de Docker y Docker Compose
docker --version
docker-compose --version

# Construir imágenes con Docker Compose (reemplaza esto con tus propios comandos de Docker Compose)
docker-compose build

# Script para iniciar el contenedor
echo -e "#!/bin/bash\n\ncd $SCRIPT_DIR\n\ndocker-compose up -d" > ~/Escritorio/Iniciar_Contenedor.sh
chmod +x ~/Escritorio/Iniciar_Contenedor.sh

# Script para detener y reiniciar el contenedor
echo -e "#!/bin/bash\n\ncd $SCRIPT_DIR\n\ndocker-compose down" > ~/Escritorio/Detener_Reiniciar_Contenedor.sh
chmod +x ~/Escritorio/Detener_Reiniciar_Contenedor.sh
