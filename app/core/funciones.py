import requests
from .models import *
from datetime import datetime



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