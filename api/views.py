from django.shortcuts import render
from rest_framework import generics, filters
from core.models import Producto
from .serializers import ProductoSerializer

class ProductoSearchAPIView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'codigo_barras']



