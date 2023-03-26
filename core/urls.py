import imp
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls import include
from .forms import MyAuthForm
from django.views.generic.base import TemplateView #import TemplateView

urlpatterns = [
    path('', LoginView.as_view(template_name='login.html', authentication_form=MyAuthForm,redirect_authenticated_user=True), name='login'),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('index', views.index, name='index'),  #add the robots.txt file
]