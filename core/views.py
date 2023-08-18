from django.shortcuts import render
from django.http import JsonResponse


# Create your views here.
def login(request):
    return render(request, 'login.html')

def index(request):
    return render(request, 'index.html')

def caja(request):
    return render(request, 'caja.html')


