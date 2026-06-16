from rest_framework import viewsets, generics, filters, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Q, Max, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal
from math import ceil
import pandas as pd
import io

from core.models import *
from .serializers import *


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.permisos == 'admin'


# ─── Auth ───────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UsuarioSerializer(user).data,
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def me_view(request):
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)


# ─── Users ──────────────────────────────────────────────────────────────────

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('-id')
    serializer_class = UsuarioSerializer
    ordering = ['-id']

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


# ─── Departments ────────────────────────────────────────────────────────────

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated]


# ─── Brands ─────────────────────────────────────────────────────────────────

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated]


# ─── Products ───────────────────────────────────────────────────────────────

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related('departamento', 'marca', 'stock').all().order_by('-id_producto')
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo_barras']
    ordering_fields = ['nombre', 'precio']
    ordering = ['-id_producto']

    @action(detail=False, methods=['get'])
    def busqueda(self, request):
        q = request.query_params.get('q', '')
        productos = Producto.objects.filter(
            Q(nombre__icontains=q) | Q(codigo_barras__icontains=q)
        )[:20]
        serializer = ProductoSimpleSerializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def rapidos(self, request):
        rapidos = ProductoRapido.objects.select_related('producto').all().order_by('orden', 'id')
        serializer = ProductoRapidoSerializer(rapidos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def agregar_rapido(self, request, pk=None):
        producto = get_object_or_404(Producto, id_producto=pk)
        rapido, created = ProductoRapido.objects.get_or_create(producto=producto)
        if not rapido.tecla:
            used = ProductoRapido.objects.exclude(tecla=None).values_list('tecla', flat=True)
            for k in '1234567890QWERTYUIOPASDFGHJKLZXCVBNM':
                if k not in used:
                    rapido.tecla = k
                    rapido.save()
                    break
        return Response(ProductoRapidoSerializer(rapido).data)

    @action(detail=True, methods=['delete'])
    def eliminar_rapido(self, request, pk=None):
        ProductoRapido.objects.filter(producto_id=pk).delete()
        return Response(status=204)

    @action(detail=False, methods=['put'])
    def config_rapido(self, request):
        data = request.data
        rapido_id = data.get('id')
        rapido = get_object_or_404(ProductoRapido, id=rapido_id)
        if 'tecla' in data:
            # Clear previous assignment of same key
            ProductoRapido.objects.filter(tecla=data['tecla']).exclude(id=rapido.id).update(tecla=None)
            rapido.tecla = data['tecla']
        if 'color' in data:
            rapido.color = data['color']
        if 'orden' in data:
            rapido.orden = data['orden']
        rapido.save()
        return Response(ProductoRapidoSerializer(rapido).data)

    @action(detail=False, methods=['post'])
    def importar(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
        df = pd.read_excel(file)
        count = 0
        for _, row in df.iterrows():
            Producto.objects.update_or_create(
                codigo_barras=str(row.get('codigo_barras', '')),
                defaults={
                    'nombre': row['nombre'],
                    'precio': row['precio'],
                    'valor_costo': row.get('valor_costo', 0),
                }
            )
            count += 1
        return Response({'imported': count})

    @action(detail=False, methods=['get'])
    def exportar(self, request):
        productos = Producto.objects.all().values()
        df = pd.DataFrame(list(productos))
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Productos')
        output.seek(0)
        from django.http import HttpResponse
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=productos.xlsx'
        return response


# ─── Cart ───────────────────────────────────────────────────────────────────

class CarritoViewSet(viewsets.ModelViewSet):
    serializer_class = CarritoItemSerializer

    def get_queryset(self):
        qs = CarritoItem.objects.filter(usuario=self.request.user).select_related('producto')
        carrito_numero = self.request.query_params.get('carrito_numero')
        if carrito_numero:
            qs = qs.filter(carrito_numero=carrito_numero)
        return qs

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def agregar(self, request):
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))
        carrito_numero = int(request.data.get('carrito_numero', 1))
        valor = request.data.get('valor')
        gramaje = request.data.get('gramaje')
        producto = get_object_or_404(Producto, id_producto=producto_id)

        # For valor products: group by same valor value
        if valor is not None:
            try:
                val_dec = Decimal(str(valor))
                existing = CarritoItem.objects.filter(
                    usuario=request.user, producto=producto,
                    carrito_numero=carrito_numero, valor=val_dec
                ).first()
                if existing:
                    existing.cantidad += cantidad
                    existing.save()
                    return Response(CarritoItemSerializer(existing, context={'request': request}).data)
                item = CarritoItem.objects.create(
                    usuario=request.user, producto=producto,
                    carrito_numero=carrito_numero, cantidad=cantidad,
                    valor=val_dec
                )
                return Response(CarritoItemSerializer(item, context={'request': request}).data)
            except: pass

        # For gramaje: always create new item per weight
        if gramaje is not None:
            try:
                item = CarritoItem.objects.create(
                    usuario=request.user, producto=producto,
                    carrito_numero=carrito_numero, cantidad=0,
                    gramaje=Decimal(str(gramaje))
                )
                return Response(CarritoItemSerializer(item, context={'request': request}).data)
            except: pass

        # Default: increment quantity
        item, created = CarritoItem.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            carrito_numero=carrito_numero,
            defaults={'cantidad': cantidad}
        )
        if not created:
            item.cantidad += cantidad
            item.save()
        return Response(CarritoItemSerializer(item, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    def vaciar(self, request):
        carrito_numero = request.data.get('carrito_numero', 1)
        CarritoItem.objects.filter(usuario=request.user, carrito_numero=carrito_numero).delete()
        return Response(status=204)

    @action(detail=False, methods=['get'])
    def numeros(self, request):
        nums = CarritoItem.objects.filter(
            usuario=request.user
        ).values_list('carrito_numero', flat=True).distinct()
        return Response(sorted(list(nums)))

    @action(detail=False, methods=['get'])
    def total(self, request):
        carrito_numero = request.query_params.get('carrito_numero', 1)
        items = CarritoItem.objects.filter(usuario=request.user, carrito_numero=carrito_numero)
        total = sum(item.subtotal() for item in items)
        return Response({'total': float(total)})

    @action(detail=False, methods=['post'])
    def nuevo(self, request):
        nums = CarritoItem.objects.filter(
            usuario=request.user
        ).values_list('carrito_numero', flat=True).distinct()
        for n in range(1, 9):
            if n not in nums:
                return Response({'carrito_numero': n})
        return Response({'error': 'limite 8 cajas'}, status=400)


# ─── Sales ──────────────────────────────────────────────────────────────────

class VentaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VentaSerializer

    def get_queryset(self):
        ultima_fecha = RegistroTransaccion.objects.aggregate(Max('fecha_ingreso'))['fecha_ingreso__max']
        qs = Venta.objects.select_related('usuario').prefetch_related(
            'ventaproducto_set__producto', 'formapago_set'
        )
        if ultima_fecha:
            qs = qs.filter(fecha_hora__gt=ultima_fecha)
        fecha = self.request.query_params.get('fecha')
        hora_inicio = self.request.query_params.get('hora_inicio')
        hora_fin = self.request.query_params.get('hora_fin')
        if fecha:
            from datetime import datetime
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
            qs = qs.filter(fecha_hora__date=fecha)
        if hora_inicio and hora_fin:
            from datetime import datetime as dt
            hi = dt.strptime(hora_inicio, "%H:%M").time()
            hf = dt.strptime(hora_fin, "%H:%M").time()
            qs = qs.filter(fecha_hora__time__range=(hi, hf))
        return qs.order_by('-fecha_hora')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_venta_api(request):
    config = Configuracion.objects.get(id=1)
    tipo_pago = request.data.get('tipo_pago')
    restante = float(request.data.get('restante', 0))
    vuelto_inicial = float(request.data.get('vuelto_inicial', 0))
    carrito_numero = int(request.data.get('carrito_numero', 1))

    items = CarritoItem.objects.filter(usuario=request.user, carrito_numero=carrito_numero)
    if not items.exists():
        return Response({'error': 'Carrito vacio'}, status=400)

    total = sum(item.subtotal() for item in items)
    venta = Venta.objects.create(usuario=request.user, total=total, vuelto=vuelto_inicial)

    for item in items:
        subtotal = item.subtotal()
        VentaProducto.objects.create(
            venta=venta, producto=item.producto,
            cantidad=item.cantidad, gramaje=item.gramaje, subtotal=subtotal
        )

    items.delete()

    if restante > 0:
        monto_efectivo_restante = abs(total - restante)
        FormaPago.objects.create(venta=venta, tipo_pago=tipo_pago, monto=restante)
        FormaPago.objects.create(venta=venta, tipo_pago="efectivo", monto=monto_efectivo_restante)
    elif tipo_pago in ("efectivo", "Efectivo Justo"):
        FormaPago.objects.create(venta=venta, tipo_pago="efectivo", monto=total)
    else:
        FormaPago.objects.create(venta=venta, tipo_pago=tipo_pago, monto=total)

    from core.impresora import abrir_caja_impresora, imprimir_ultima_id
    if tipo_pago == "efectivo" or tipo_pago == "Efectivo Justo" or restante > 0:
        abrir_caja_impresora()

    if config.imprimir != 'no':
        imprimir_ultima_id()

    if request.user.ventas_config == "pruebas":
        venta.delete()

    return Response(VentaSerializer(venta).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_venta_api(request, venta_id):
    config = Configuracion.objects.get(id=1)
    venta = get_object_or_404(Venta, id=venta_id)
    clave = request.data.get('clave_anulacion', '')
    if clave == config.clave_anulacion or clave == request.user.clave_anulacion:
        venta.delete()
        return Response(status=204)
    return Response({'error': 'Clave incorrecta'}, status=403)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventas_respaldo_api(request):
    qs = VentaRespaldo.objects.select_related('usuario').all()
    serializer = VentaRespaldoSerializer(qs, many=True)
    return Response(serializer.data)


# ─── Configuration ──────────────────────────────────────────────────────────

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def configuracion_api(request):
    config = Configuracion.objects.get(id=1)
    if request.method == 'PUT':
        serializer = ConfiguracionSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    serializer = ConfiguracionSerializer(config)
    return Response(serializer.data)


# ─── Daily Box ──────────────────────────────────────────────────────────────

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def caja_diaria_api(request):
    caja = CajaDiaria.objects.get(id=1)
    if request.method == 'PUT':
        serializer = CajaDiariaSerializer(caja, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    return Response(CajaDiariaSerializer(caja).data)


# ─── Expenses ───────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def gastos_api(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['usuario'] = request.user.id
        serializer = GastoCajaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    ultima_fecha = RegistroTransaccion.objects.aggregate(Max('fecha_ingreso'))['fecha_ingreso__max']
    qs = GastoCaja.objects.select_related('usuario').all()
    if ultima_fecha:
        qs = qs.filter(fecha_hora__gte=ultima_fecha)
    return Response(GastoCajaSerializer(qs, many=True).data)


# ─── Reports ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def informe_general_api(request):
    caja_diaria = CajaDiaria.objects.get(id=1)
    config = Configuracion.objects.get(id=1)
    try:
        ultima_fecha = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
    except RegistroTransaccion.DoesNotExist:
        ultima_fecha = None

    ventas = Venta.objects.filter(fecha_hora__gte=ultima_fecha) if ultima_fecha else Venta.objects.all()
    gastos = GastoCaja.objects.filter(fecha_hora__gte=ultima_fecha) if ultima_fecha else GastoCaja.objects.all()

    total_ventas = ventas.aggregate(Sum('total'))['total__sum'] or 0
    monto_efectivo = FormaPago.objects.filter(venta__in=ventas, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_debito = FormaPago.objects.filter(venta__in=ventas, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_transferencia = FormaPago.objects.filter(venta__in=ventas, tipo_pago='transferencia').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_credito = FormaPago.objects.filter(venta__in=ventas, tipo_pago='credito').aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or 0
    caja_que_deberia = monto_efectivo + caja_diaria.monto - caja_diaria.retiro - total_gastos

    ventas_por_depto = VentaProducto.objects.filter(venta__in=ventas).values(
        'producto__departamento__nombre'
    ).annotate(
        total=Sum('subtotal')
    )

    return Response({
        'total_ventas': total_ventas,
        'monto_efectivo': monto_efectivo,
        'monto_debito': monto_debito,
        'monto_transferencia': monto_transferencia,
        'monto_credito': monto_credito,
        'monto_retiro': caja_diaria.retiro,
        'monto_caja': caja_diaria.monto,
        'total_gastos': total_gastos,
        'caja_que_deberia': caja_que_deberia,
        'ventas_por_departamento': ventas_por_depto,
        'decimales': config.decimales,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cerrar_caja_api(request, monto_en_la_caja):
    caja_diaria = CajaDiaria.objects.get(id=1)
    try:
        ultima_fecha = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
    except RegistroTransaccion.DoesNotExist:
        ultima_fecha = None

    ventas = Venta.objects.filter(fecha_hora__gte=ultima_fecha) if ultima_fecha else Venta.objects.all()

    monto_efectivo = FormaPago.objects.filter(venta__in=ventas, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_credito = FormaPago.objects.filter(venta__in=ventas, tipo_pago='credito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_debito = FormaPago.objects.filter(venta__in=ventas, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_transferencia = FormaPago.objects.filter(venta__in=ventas, tipo_pago='transferencia').aggregate(Sum('monto'))['monto__sum'] or 0

    RegistroTransaccion.objects.create(
        monto_total=ventas.aggregate(Sum('total'))['total__sum'] or 0,
        monto_efectivo=monto_efectivo,
        monto_credito=monto_credito,
        monto_debito=monto_debito,
        monto_transferencia=monto_transferencia,
        monto_retiro=caja_diaria.retiro,
        valor_caja_diaria=caja_diaria.monto,
    )

    caja_diaria.monto = monto_en_la_caja
    caja_diaria.retiro = 0
    caja_diaria.save()

    return Response({'status': 'caja cerrada'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_dia_especifico_api(request):
    fecha = request.query_params.get('fecha')
    hora_inicio = request.query_params.get('hora_inicio')
    hora_fin = request.query_params.get('hora_fin')

    ventas = Venta.objects.all()
    if fecha:
        from datetime import datetime
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        ventas = ventas.filter(fecha_hora__date=fecha)
    if hora_inicio and hora_fin:
        from datetime import datetime as dt
        hi = dt.strptime(hora_inicio, "%H:%M").time()
        hf = dt.strptime(hora_fin, "%H:%M").time()
        ventas = ventas.filter(fecha_hora__time__range=(hi, hf))

    return Response({
        'total': ventas.aggregate(Sum('total'))['total__sum'] or 0,
        'count': ventas.count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cierres_caja_api(request):
    cierres = RegistroTransaccion.objects.all().order_by('-fecha_ingreso')
    from .serializers import RegistroTransaccionSerializer
    return Response(RegistroTransaccionSerializer(cierres, many=True).data)


# ─── Cash Reconciliation (Cuadre) ───────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cuadrar_api(request):
    config = Configuracion.objects.get(id=1)
    caja_diaria = CajaDiaria.objects.get(id=1)
    serializer = BilletesMonedasSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data
    total_efectivo = sum([
        data['monedas_10'], data['monedas_50'], data['monedas_100'],
        data['monedas_500'], data['billetes_1000'], data['billetes_2000'],
        data['billetes_5000'], data['billetes_10000'], data['billetes_20000'],
    ])
    maquinas_debito = data['maquinas_debito']

    try:
        ultima_fecha = RegistroTransaccion.objects.latest('fecha_ingreso').fecha_ingreso
    except RegistroTransaccion.DoesNotExist:
        ultima_fecha = None

    ventas = Venta.objects.filter(fecha_hora__gte=ultima_fecha) if ultima_fecha else Venta.objects.all()
    gastos = GastoCaja.objects.filter(fecha_hora__gte=ultima_fecha) if ultima_fecha else GastoCaja.objects.all()

    monto_efectivo = FormaPago.objects.filter(venta__in=ventas, tipo_pago='efectivo').aggregate(Sum('monto'))['monto__sum'] or 0
    monto_debito = FormaPago.objects.filter(venta__in=ventas, tipo_pago='debito').aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or 0

    monto_que_deberia_dar = monto_efectivo + caja_diaria.monto - caja_diaria.retiro - total_gastos
    monto_faltante_efectivo = monto_que_deberia_dar - total_efectivo
    maquina_faltante = monto_debito - maquinas_debito

    Cuadre.objects.create(usuario=request.user)

    return Response({
        'total_efectivo_esperado': monto_que_deberia_dar,
        'total_efectivo_contado': total_efectivo,
        'diferencia_efectivo': monto_faltante_efectivo,
        'estado_efectivo': 'sobrante' if monto_faltante_efectivo < 0 else 'faltante',
        'debito_esperado': monto_debito,
        'debito_maquinas': maquinas_debito,
        'diferencia_debito': maquina_faltante,
        'estado_debito': 'sobrante' if maquina_faltante < 0 else 'faltante',
        'billetes': data,
    })


# ─── Printer ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def probar_impresora_api(request):
    from core.impresora import probar_impresora
    from django.http import HttpResponse
    return probar_impresora(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estado_impresora_api(request):
    from core.middleware import verificar_impresora_conectada
    resultado = verificar_impresora_conectada()
    return Response({'conectada': resultado is not None, 'dispositivo': resultado})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verificar_clave_api(request):
    clave = request.data.get('clave', '').strip()
    if not clave:
        return Response({'valida': False, 'error': 'Ingresa una clave'}, status=400)

    config = Configuracion.objects.get(id=1)
    usuario_valido = None

    if config.tipo_autorizacion == 'cualquier':
        usuarios = Usuario.objects.filter(clave_anulacion=clave, is_active=True)
        if usuarios.exists():
            usuario_valido = usuarios.first()
    elif config.tipo_autorizacion == 'propio':
        if request.user.clave_anulacion == clave:
            usuario_valido = request.user

    if usuario_valido:
        return Response({
            'valida': True,
            'usuario': usuario_valido.username,
            'usuario_id': usuario_valido.id,
        })
    return Response({'valida': False, 'error': 'Clave invalida'}, status=403)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def abrir_caja_api(request):
    from core.impresora import abrir_caja_impresora, _enviar_a_impresora
    clave = request.data.get('clave', '').strip()
    config = Configuracion.objects.get(id=1)
    autorizado = False

    if config.tipo_autorizacion == 'cualquier':
        if Usuario.objects.filter(clave_anulacion=clave, is_active=True).exists():
            autorizado = True
    elif config.tipo_autorizacion == 'propio':
        if request.user.clave_anulacion == clave:
            autorizado = True

    if not autorizado:
        return Response({'error': 'Clave incorrecta'}, status=403)

    try:
        _enviar_a_impresora(b'\x1B\x70\x00\x50\x50')
        return Response({'exito': True, 'mensaje': 'Cajon abierto exitosamente'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ─── Updates ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_updates_api(request):
    import requests as req
    owner = 'gladoncio'
    repo = 'caja_registradora'
    api_url = f'https://api.github.com/repos/{owner}/{repo}/releases'
    try:
        response = req.get(api_url)
        releases = response.json() if response.ok else []
        return Response({
            'releases': [{
                'tag_name': r.get('tag_name'),
                'published_at': r.get('published_at'),
                'body': r.get('body'),
            } for r in releases if not r.get('draft')],
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ─── Metodos de pago ────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metodos_pago_api(request):
    return Response([
        {'id': 'efectivo', 'nombre': 'Efectivo'},
        {'id': 'efectivo_justo', 'nombre': 'Efectivo Justo'},
        {'id': 'transferencia', 'nombre': 'Transferencia'},
        {'id': 'debito', 'nombre': 'Debito'},
    ])
