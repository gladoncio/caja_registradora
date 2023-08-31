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

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)