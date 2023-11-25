import requests
from datetime import datetime
import os
import subprocess

try:
    # Guarda los cambios locales antes de hacer checkout
    subprocess.run(["git", "stash"], check=True)

    # Vuelve a la rama principal
    subprocess.run(["git", "checkout", "main"], check=True)

    # Obtiene los últimos cambios de la rama principal
    subprocess.run(["git", "pull", "origin", "main"], check=True)

    message = f"volviendo a la ultima update."

except subprocess.CalledProcessError as e:
    message = f"Error al hacer checkout: {e}"

# Restaura los cambios locales después de hacer checkout
subprocess.run(["git", "stash", "apply"], check=True)
