#!/bin/bash

# Obtener el nombre de usuario principal
USERNAME="$SUDO_USER"

# Si SUDO_USER está vacío, intentar obtener el nombre de usuario actual
if [ -z "$USERNAME" ]; then
    USERNAME=$(logname)
fi

echo "Nombre de usuario: $USERNAME"

# Obtener la ruta del directorio actual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Directorio del script: $SCRIPT_DIR"

# Ruta del escritorio del usuario
DESKTOP_DIR="/home/$USERNAME/Desktop"

echo "Directorio del escritorio: $DESKTOP_DIR"

# Crear el directorio Escritorio si no existe
mkdir -p "$DESKTOP_DIR"

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

sudo usermod -aG docker $USERNAME

# Construir imágenes con Docker Compose (reemplaza esto con tus propios comandos de Docker Compose)
docker-compose build

# Script para iniciar el contenedor
echo -e "#!/bin/bash\n\ncd $SCRIPT_DIR\n\ndocker-compose up -d\nxdg-open http://localhost:8000" > "$DESKTOP_DIR/Iniciar_caja.sh"
chmod +x "$DESKTOP_DIR/Iniciar_caja.sh"

# Script para detener y reiniciar el contenedor
echo -e "#!/bin/bash\n\ncd $SCRIPT_DIR\n\ndocker-compose down" > "$DESKTOP_DIR/Detener_caja.sh"
chmod +x "$DESKTOP_DIR/Detener_caja.sh"