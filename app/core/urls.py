import imp
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import include
from .forms import MyAuthForm
from django.views.generic.base import TemplateView #import TemplateView
from .views import *

urlpatterns = [
    path('login', LoginView.as_view(template_name='login.html', authentication_form=MyAuthForm,redirect_authenticated_user=True), name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('', views.index, name='index'),
    path('caja/', views.caja, name='caja'),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('agregar_producto_al_carrito/<id_producto>/', views.agregar_producto_al_carrito, name='agregar_producto_al_carrito'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('ventas/', views.listar_ventas, name='listar_ventas'),  # Agrega esta línea
    path('venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('informe-general/', views.informe_general, name='informe_general'),
    path('cerrar_caja/<monto_en_la_caja>', views.cerrar_caja, name='cerrar_caja'),
    path('editar-caja-diaria/', views.editar_monto_caja_diaria, name='editar_caja_diaria'),
    path('cuadrar/', views.cuadrar, name='cuadrar'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('imprimir/', views.imprimir, name='imprimir'),
    path('verificar-actualizaciones/', check_updates, name='verificar-actualizaciones'),
    path('abrir-caja/', views.abrir_caja, name='abrir-caja'),
    path('generate_barcode/', views.generate_barcode, name='generate_barcode'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('imprimir_boleta/<int:venta_id>/', views.imprimir_boleta, name='imprimir_boleta'),
    path('seleccionar_metodo_pago/', views.seleccionar_metodo_pago, name='seleccionar_metodo_pago'),
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
    path('ingresar_monto_efectivo/', views.ingresar_monto_efectivo, name='ingresar_monto_efectivo'),
    path('seleccionar_metodo_pago_resto/<total>/<monto_efectivo>/', seleccionar_metodo_pago_resto, name='seleccionar_metodo_pago_resto'),
    path('procesar_pago_restante/<metodo_pago>/<restante>/', views.procesar_pago_restante, name='procesar_pago_restante'),
    path('ventas-respaldo/', views.listar_ventas_respaldo, name='listar_ventas_respaldo'),
    path('ventas-respaldo/<int:venta_respaldo_id>/', views.detalle_venta_respaldo, name='detalle_venta_respaldo'),
    path('eliminar-venta/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('ingresar-gasto/', views.ingresar_gasto, name='ingresar_gasto'),
    path('gastos/', views.lista_gastos, name='lista_gastos'),
    path('configuracion/edit/', ConfiguracionUpdateView.as_view(), name='config'),
    path('cambiar_clave/<int:user_id>/', views.cambiar_clave_usuario, name='cambiar_clave_usuario'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('lista_usuarios_desabilitados/', views.lista_usuarios_desabilitados, name='lista_usuarios_desabilitados'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/activar/<int:user_id>/', views.activar_usuario, name='activar_usuario'),
    path('generar_codigo_ean13/', views.generar_y_imprimir_codigo_ean13, name='generar_codigo_ean13'),
    path('generar_venta/<parametro1>/<parametro2>/<parametro3>/<parametro4>', views.generar_venta, name='generar_venta'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('productos/', ProductoListView.as_view(), name='producto-list'),
    path('producto/editar/<int:pk>/', ProductoEditarView.as_view(), name='producto-editar'),  # Define la URL de edición
    path('impresora-no-conectada/', impresora_no_conectada, name='impresora_no_conectada'),
    path('impresora-si-conectada/', impresora_si_conectada, name='impresora_si_conectada'),
    path('cambiar_usuario/<int:usuario_id>/', cambiar_usuario, name='cambiar_usuario'),
    path('cambiar_clave_anulacion/<int:usuario_id>/', cambiar_clave_anulacion, name='cambiar_clave_anulacion'),
    
]

    


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)