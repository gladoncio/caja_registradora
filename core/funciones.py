from .views import *
from django.shortcuts import render, redirect, get_object_or_404
from steamauth import auth, get_uid
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from .forms import *
from django.contrib import messages
from .models import Usuario as usu, SmAdmins as sm_admins, Respuestas as res, Preguntas as pre, Player as pl,CustomChatcolors as cl
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from steamid_converter import Converter
from django.urls import reverse
import os
from datetime import datetime
import validators
import urllib.request, json
from datetime import datetime
import requests
from django.core.paginator import Paginator

def variables_globales(request):
    avatar_cuenta = ""
    steamid_cuenta = ""
    rango_cuenta = "Usuario"
    if request.user.is_authenticated:
        steamid_cuenta = request.user.steam_id
        if steamid_cuenta!="":
            steamid64 = detectardato(steamid_cuenta)
            datos = traer_datos(steamid64)
            avatar_cuenta = datos['avatarfull']
            try:
                rango = get_object_or_404(sm_admins, identity = steamid_cuenta)
                rango_cuenta = rango.name
            except:
                print("dato no existe")
    context = {'avatar_cuenta' : avatar_cuenta, 'steamid_cuenta' : steamid_cuenta, 'rango_cuenta' : rango_cuenta}
    return context

def detectardato(dato):
    dato = dato.strip()
    if dato.startswith("STEAM_") or dato.startswith("[U"):
        steamid64 = Converter.to_steamID64(dato, as_int=False)
        return steamid64
    elif validators.url(dato):
        if dato.endswith("/"):
            dato = dato.rstrip(dato[-1])
        subdirname = os.path.basename(os.path.dirname(dato))
        if subdirname=="id":
            custom = os.path.basename(dato)
            url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=9D6D8348D31393D6E89D49F1C933F0E7&vanityurl={custom}"
            data = urllib.request.urlopen(url).read()
            output = json.loads(data)
            return output['response']['steamid']
        else:
            steamid64 = os.path.basename(dato)
            return steamid64
    elif len(dato)==17:
        return dato
    else:
        return "No"

def traer_datos(id):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=9D6D8348D31393D6E89D49F1C933F0E7&steamids={id}"
    data = urllib.request.urlopen(url).read()
    output = json.loads(data)
    array = output['response']['players'][0]
    return array





def variables_views(request):
    avatar_cuenta = ""
    steamid_cuenta = ""
    rango_cuenta = "Usuario"
    if request.user.is_authenticated:
        steamid_cuenta = request.user.steam_id
        if steamid_cuenta!="":
            try:
                rango = get_object_or_404(sm_admins, identity = steamid_cuenta)
                rango_cuenta = rango.name
            except:
                print("dato no existe")
    return rango_cuenta


