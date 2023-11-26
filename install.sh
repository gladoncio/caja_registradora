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

RUTE="/caja/"

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
echo -e "#!/bin/bash\n\ncd $RUTE" > "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "PRINTER_DEVICES=\$(ls /dev/usb/lp*)\n" >> "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "if [ -z \"\$PRINTER_DEVICES\" ]; then\n" >> "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "    zenity --error --text='No se encontraron impresoras conectadas en /dev/usb/. No se iniciará el contenedor.'\n" >> "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "    exit 1\n" >> "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "fi\n" >> "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "docker-compose up -d\nzenity --info --text='Iniciando el contenedor, por favor espera 5 segundos...'\n" >> "$DESKTOP_DIR/Iniciar_caja.sh"
echo -e "sleep 10\nzenity --info --text='El contenedor se ha iniciado abriendo en el navegador.' &\nxdg-open http://localhost:8000" >> "$DESKTOP_DIR/Iniciar_caja.sh"
chmod +x "$DESKTOP_DIR/Iniciar_caja.sh"

# Script para detener y reiniciar el contenedor
echo -e "#!/bin/bash\n\ncd $RUTE\nzenity --info --text='Deteniendo el contenedor, por favor espera 3 segundos...'\ndocker-compose down\nsleep 3\nzenity --info --text='El contenedor se ha detenido correctamente.'" > "$DESKTOP_DIR/Detener_caja.sh"
chmod +x "$DESKTOP_DIR/Detener_caja.sh"

PYTHON_PATH=$(which python3)

echo -e "#!/bin/bash\n\ncd $RUTE" > "caja/update.sh"
echo -e "\n$PYTHON_PATH update.sh" >> "caja/update.sh"

sudo chmod +x /caja/update.sh

# Confirmar si el usuario desea reiniciar
(crontab -l 2>/dev/null ; echo "*/2 * * * * /caja/update.sh > /caja/registro.log 2>&1") | crontab - && echo "Tarea agregada correctamente" || echo "Error al agregar la tarea" > salida_crontab 2>&1

read -p "Se necesita reiniciar ¿Deseas reiniciar el sistema ahora? (y/n): " reiniciar
if [ "$reiniciar" == "y" ]; then
    sudo reboot
else
    echo "No se reiniciará el sistema."
fi

