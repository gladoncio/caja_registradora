from django.contrib import admin
from .models import Stock, Usuario, Departamento, Marca, Producto

admin.site.register(Usuario)
admin.site.register(Departamento)
admin.site.register(Marca)
admin.site.register(Producto)
admin.site.register(Stock)
