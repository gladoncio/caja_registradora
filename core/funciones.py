import requests
from .models import *
from datetime import datetime



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
    
# def verificar_actualizacion(request):
#     context = {'actualizado' : "si"}
#     actualizacion = ActualizacionModel.objects.first()
    

#     if actualizacion:
#         # Obtiene la fecha guardada en la tabla
#         fecha_guardada = actualizacion.fecha_actualizacion

#         try:
#             # Obtiene la fecha de la última versión en GitHub
#             latest_release_date = get_github_latest_release_date()
#             fecha_github = datetime.strptime(latest_release_date, "%Y-%m-%dT%H:%M:%SZ")

            
#             if fecha_guardada >= fecha_github:
#                 context = {'actualizado' : "no"}
#                 return context

#         except Exception as e:
#             # Maneja errores en la obtención de la fecha de GitHu
#             return context

#     # Si no hay registros en la tabla, asumimos que no estamos actualizados
#     return context
