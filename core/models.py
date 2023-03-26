from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    permisos = models.CharField(max_length=40,null=True, verbose_name="Permiso",default="1")
    rut = models.CharField(max_length=40,null=True, verbose_name="Rut",default="")

