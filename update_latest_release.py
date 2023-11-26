import requests
from datetime import datetime
import os
import subprocess

def check_github_version():
    url = "https://api.github.com/repos/gladoncio/caja_registradora/releases/latest"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        latest_version = data["tag_name"]
        return latest_version
    else:
        # Manejar el error, puedes imprimir un mensaje o levantar una excepción según tus necesidades
        return None
    
latest_release_name = check_github_version()

if latest_release_name is not None:
    try:
        # Ejecuta el comando git checkout
        subprocess.run(["git", "checkout", latest_release_name], check=True)

        # Guarda la fecha, hora y versión en un archivo
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open("update_info.txt", "a") as file:
            file.write(f"{timestamp} - Versión actualizada a {latest_release_name}\n")

        message = f"Checkout exitoso a la última release ({latest_release_name})."

    except subprocess.CalledProcessError as e:
        message = f"Error al hacer checkout: {e}"
else:
    message = "No se pudo obtener la última release desde GitHub."
