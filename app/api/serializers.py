from rest_framework import serializers
from core.models import *
from django.contrib.auth import authenticate


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'rut', 'permisos', 'ventas_config', 'foto_perfil', 'clave_anulacion', 'is_active']
        read_only_fields = ['id']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'email', 'rut', 'permisos', 'clave_anulacion']

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Credenciales invalidas")


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'


class ProductoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id_producto', 'nombre', 'precio', 'codigo_barras', 'tipo_venta']


class ProductoRapidoSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProductoRapido
        fields = ['id', 'producto', 'producto_id', 'tecla', 'color', 'orden']


class CarritoItemSerializer(serializers.ModelSerializer):
    producto = ProductoSimpleSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CarritoItem
        fields = ['id', 'usuario', 'carrito_numero', 'producto', 'producto_id', 'cantidad', 'gramaje', 'valor', 'fecha_agregado', 'subtotal']
        read_only_fields = ['id', 'usuario', 'fecha_agregado', 'subtotal']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = '__all__'


class VentaProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = VentaProducto
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'gramaje', 'subtotal']


class FormaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = ['id', 'tipo_pago', 'monto']


class VentaSerializer(serializers.ModelSerializer):
    productos = VentaProductoSerializer(source='ventaproducto_set', many=True, read_only=True)
    formas_pago = FormaPagoSerializer(source='formapago_set', many=True, read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'fecha_hora', 'total', 'vuelto', 'usuario', 'usuario_username', 'productos', 'formas_pago']


class VentaCreateSerializer(serializers.Serializer):
    tipo_pago = serializers.CharField()
    restante = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    vuelto_inicial = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    carrito_numero = serializers.IntegerField()


class VentaRespaldoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = VentaRespaldo
        fields = '__all__'


class RegistroTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroTransaccion
        fields = '__all__'


class CajaDiariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CajaDiaria
        fields = '__all__'


class GastoCajaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = GastoCaja
        fields = '__all__'


class RetiroCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetiroCaja
        fields = '__all__'


class CuadreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuadre
        fields = '__all__'


class BilletesMonedasSerializer(serializers.Serializer):
    monedas_10 = serializers.IntegerField(default=0)
    monedas_50 = serializers.IntegerField(default=0)
    monedas_100 = serializers.IntegerField(default=0)
    monedas_500 = serializers.IntegerField(default=0)
    billetes_1000 = serializers.IntegerField(default=0)
    billetes_2000 = serializers.IntegerField(default=0)
    billetes_5000 = serializers.IntegerField(default=0)
    billetes_10000 = serializers.IntegerField(default=0)
    billetes_20000 = serializers.IntegerField(default=0)
    maquinas_debito = serializers.IntegerField(default=0)


class ActualizacionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActualizacionModel
        fields = '__all__'
