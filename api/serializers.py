from rest_framework import serializers
from core.models import Producto, Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['cantidad']

class ProductoSerializer(serializers.ModelSerializer):
    cantidad = StockSerializer(source='stock', read_only=True)  # Incluir la cantidad desde Stock

    class Meta:
        model = Producto
        fields = '__all__'
