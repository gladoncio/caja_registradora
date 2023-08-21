from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import *
from .models import *
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.

def login(request):
    return render(request, 'login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect(index)


@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')

def caja(request):
    return render(request, 'caja.html')