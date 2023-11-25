import requests
from .models import *
from datetime import datetime




def obtener_ultima_release(usuario, repositorio):
    url = f'https://api.github.com/repos/{usuario}/{repositorio}/releases/latest'
    respuesta = requests.get(url)
    datos = respuesta.json()
    return datos['tag_name']