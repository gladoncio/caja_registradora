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
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('', views.index, name='index'),
    path('caja/', views.caja, name='caja'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('generar_venta/<parametro1>/<parametro2>/<parametro3>', views.generar_venta, name='generar_venta'),
    path('ventas/', views.listar_ventas, name='listar_ventas'),  # Agrega esta línea
    path('venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('informe-general/', views.informe_general, name='informe_general'),
    path('cerrar_caja/', views.cerrar_caja, name='cerrar_caja'),
    path('editar-caja-diaria/', views.editar_monto_caja_diaria, name='editar_caja_diaria'),
    path('cuadrar/', views.cuadrar, name='cuadrar'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('imprimir/', views.imprimir, name='imprimir'),
    path('abrir_caja/', views.abrir_caja, name='abrir_caja'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)