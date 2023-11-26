from datetime import datetime
import os
import subprocess
import requests

def check_github_version():
    url = "https://api.github.com/repos/gladoncio/caja_registradora/releases/latest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        latest_version = data["tag_name"]
        return latest_version
    else:
        return None

latest_release_name = check_github_version()

if latest_release_name is not None:
    try:
        subprocess.run(["git", "fetch", "--all"])

        # Obtener la versión almacenada en el archivo
        file_path = "update_info.txt"
        stored_version = None
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r") as file:
                lines = file.readlines()
                stored_version_line = lines[-1].strip()
                stored_version = stored_version_line.split()[-1]

        # Comprobar si la versión almacenada es la misma que la última versión de GitHub
        if stored_version != latest_release_name:
            subprocess.run(["git", "reset", "--hard", f"origin/{latest_release_name}"])
            subprocess.run(["git", "checkout", "-f", latest_release_name], check=True)

            # Guarda la fecha, hora y versión en un archivo (abrir en modo "w" en lugar de "a")
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            with open(file_path, "w") as file:
                file.write(f"{timestamp} - Versión actualizada a {latest_release_name}\n")

            message = f"Checkout exitoso a la última release ({latest_release_name})."
        else:
            message = f"La versión almacenada en el archivo ya es la última ({latest_release_name}). No se ha actualizado."

    except subprocess.CalledProcessError as e:
        message = f"Error al hacer checkout: {e}"
else:
    message = "No se pudo obtener la última release desde GitHub."

print(message)
