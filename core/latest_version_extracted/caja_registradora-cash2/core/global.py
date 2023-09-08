from .models import *
import requests
from django.shortcuts import render, redirect, get_object_or_404

def variables_globales(request):
    configuracion = Configuracion.objects.first()  # Suponiendo que tienes una única configuración
    context = {'configuracion' : configuracion}
    return context

