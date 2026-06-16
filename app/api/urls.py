from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'marcas', MarcaViewSet, basename='marca')
router.register(r'carrito', CarritoViewSet, basename='carrito')
router.register(r'ventas', VentaViewSet, basename='venta')

app_name = 'api'

urlpatterns = [
    # Auth
    path('login/', login_view, name='login'),
    path('me/', me_view, name='me'),

    # Ventas actions
    path('ventas/generar/', generar_venta_api, name='generar-venta'),
    path('ventas/<int:venta_id>/eliminar/', eliminar_venta_api, name='eliminar-venta'),
    path('ventas/respaldo/', ventas_respaldo_api, name='ventas-respaldo'),

    # Config
    path('configuracion/', configuracion_api, name='configuracion'),

    # Caja diaria
    path('caja-diaria/', caja_diaria_api, name='caja-diaria'),
    path('caja-diaria/cerrar/<monto_en_la_caja>/', cerrar_caja_api, name='cerrar-caja'),
    path('caja-diaria/abrir/', abrir_caja_api, name='abrir-caja'),

    # Gastos
    path('gastos/', gastos_api, name='gastos'),

    # Reportes
    path('reportes/general/', informe_general_api, name='informe-general'),
    path('reportes/dia-especifico/', reporte_dia_especifico_api, name='reporte-dia'),
    path('reportes/cierres/', cierres_caja_api, name='cierres-caja'),
    path('reportes/cuadrar/', cuadrar_api, name='cuadrar'),

    # Autorizacion
    path('autorizar/', verificar_clave_api, name='verificar-clave'),

    # Impresora
    path('impresora/probar/', probar_impresora_api, name='probar-impresora'),
    path('impresora/estado/', estado_impresora_api, name='estado-impresora'),

    # Actualizaciones
    path('actualizaciones/', check_updates_api, name='actualizaciones'),

    # Metodos de pago
    path('metodos-pago/', metodos_pago_api, name='metodos-pago'),

    # Router URLs
    path('', include(router.urls)),
]
