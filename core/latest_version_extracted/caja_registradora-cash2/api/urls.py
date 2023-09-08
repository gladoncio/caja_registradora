from django.urls import path
from .views import ProductoSearchAPIView

app_name = 'api'

urlpatterns = [
    path('busqueda/', ProductoSearchAPIView.as_view(), name='producto-search'),
]