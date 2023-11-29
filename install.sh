#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse con privilegios de superusuario."
    exit 1
fi

# Obtener el nombre de usuario principal
USERNAME="$SUDO_USER"

# Si SUDO_USER está vacío, intentar obtener el nombre de usuario actual
if [ -z "$USERNAME" ]; then
    USERNAME=$(logname)
fi

echo "Nombre de usuario: $USERNAME"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Directorio del script: $SCRIPT_DIR"

# Obtener la ruta del escritorio del usuario actual
DESKTOP_DIR=$(sudo -u $USERNAME xdg-user-dir DESKTOP)

echo "Directorio del escritorio: $DESKTOP_DIR"

RUTE="/caja"

# Crear la nueva ruta si no existe
mkdir -p "$RUTE"

# Copiar archivos al nuevo directorio
sudo cp -r "$SCRIPT_DIR"/{.,}* "$RUTE"

# Eliminar todo en el directorio excepto install.sh
sudo rm -r "$SCRIPT_DIR"

sudo chmod -R 777 "$RUTE"

cd "$RUTE"

sudo chmod -R 7777 .git

# Actualizar los paquetes del sistema
sudo apt update
sudo apt upgrade -y

sudo apt install curl

sudo apt install zenity

# Instalar Docker
sudo apt install -y docker.io

# Iniciar y habilitar el servicio Docker
sudo systemctl start docker
sudo systemctl enable docker

# Instalar Docker Compose
sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar la instalación de Docker y Docker Compose
docker --version
docker-compose --version

sudo usermod -aG docker $USERNAME

# Construir imágenes con Docker Compose (reemplaza esto con tus propios comandos de Docker Compose)
docker-compose build

# Script para iniciar el contenedor
echo -e "#!/bin/bash\n\ncd $RUTE" > "$RUTE/Iniciar_caja.sh"
echo -e "docker-compose up -d" >> "$RUTE/Iniciar_caja.sh"
echo -e "sleep 3 & \nxdg-open http://localhost:8000" >> "$RUTE/Iniciar_caja.sh"
chmod +x "$RUTE/Iniciar_caja.sh"

# Script para detener y reiniciar el contenedor
echo -e "#!/bin/bash\n\ncd $RUTE\ndocker-compose down\nsleep 3\nzenity --info --text='El contenedor se ha detenido correctamente.'" > "$DESKTOP_DIR/Detener_caja.sh"
chmod +x "$DESKTOP_DIR/Detener_caja.sh"

PYTHON_PATH=$(which python3)

echo -e "#!/bin/bash\n\ncd $RUTE" > "/caja/update.sh"
echo -e "\n$PYTHON_PATH update_latest_release.py" >> "/caja/update.sh"

sudo chmod +x /caja/update.sh

# Línea que deseas agregar al crontab
CRON_LINE="*/30 * * * * /caja/update.sh > /caja/registro.log 2>&1"

# Verificar si la línea ya está en el crontab
if (crontab -l 2>/dev/null | grep -Fxq "$CRON_LINE"); then
    echo "La tarea ya está programada en el crontab."
else
    (crontab -l 2>/dev/null ; echo "$CRON_LINE") | crontab - && echo "Tarea agregada correctamente" || echo "Error al agregar la tarea" > salida_crontab 2>&1
fi

# Crear el archivo de servicio systemd
SERVICE_FILE="/etc/systemd/system/caja.service"

echo "[Unit]" > "$SERVICE_FILE"
echo "Description=Descripción de tu servicio" >> "$SERVICE_FILE"
echo "After=network.target" >> "$SERVICE_FILE"
echo "" >> "$SERVICE_FILE"
echo "[Service]" >> "$SERVICE_FILE"
echo "ExecStart=/caja/Iniciar_caja.sh" >> "$SERVICE_FILE"
echo "Restart=always" >> "$SERVICE_FILE"
echo "User=root" >> "$SERVICE_FILE"
echo "" >> "$SERVICE_FILE"
echo "[Install]" >> "$SERVICE_FILE"
echo "WantedBy=default.target" >> "$SERVICE_FILE"

# Recargar systemd
sudo systemctl daemon-reload

# Iniciar y habilitar el servicio
sudo systemctl start caja
sudo systemctl enable caja

read -p "Se necesita reiniciar ¿Deseas reiniciar el sistema ahora? (y/n): " reiniciar
if [ "$reiniciar" == "y" ]; then
    sudo reboot
else
    echo "No se reiniciará el sistema."
fi

