from .models import *
import requests
from django.shortcuts import render, redirect, get_object_or_404

def variables_globales(request):
    configuracion = Configuracion.objects.first()  # Suponiendo que tienes una única configuración
    version = ActualizacionModel.objects.first()
    context = {'configuracion' : configuracion,'version' : version}
    return context

# def check_github_version():
#     url = "https://api.github.com/repos/gladoncio/caja_registradora/releases/latest"
#     response = requests.get(url)
#     data = response.json()
#     latest_version = data["tag_name"]
#     return latest_version

# def get_github_latest_release_date():
#     try:
#         url = "https://api.github.com/repos/gladoncio/caja_registradora/releases/latest"
#         response = requests.get(url)
#         data = response.json()
#         latest_release_date = data["published_at"]
#         return latest_release_date
#     except Exception as e:
#         # Maneja cualquier error de solicitud aquí
#         return None  # En caso de error, devuelve None o una fecha predeterminada
    
