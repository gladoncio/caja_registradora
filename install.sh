#!/bin/bash

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
