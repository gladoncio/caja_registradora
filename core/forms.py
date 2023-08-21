from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.forms import ModelForm, fields, Form
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput


class UsuarioRegisterForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(
    attrs={'class':'form-control form-control-lg','type':'password', 'name': 'password','placeholder':'Password'}),
    label='')
    password2 = forms.CharField(widget=forms.PasswordInput(
    attrs={'class':'form-control form-control-lg','type':'password', 'name': 'password','placeholder':'Password'}),
    label='',
    error_messages = {
        'error_messages': 'padada',
        'invalid': 'fields format is not valid',
        'max_length': 'max_length is 30 chars',
        'min_length': 'password should be at least 8 Chars',
        'password_mismatch' : 'The twdada.',
        })
    class Meta:
        model = Usuario
        fields = ['username','email','password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
                    'password1': forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
                    'password2': forms.PasswordInput(attrs={'class': 'form-control form-control-lg' }),
                    }
        error_messages_email = {
        'required': 'Ingrese un dato',
        'invalid': 'Formato invalido',
        'max_length': 'max length is 40 chars',
        }
        error_messages = {
        'required': 'please Fill-out this field',
        'invalid': 'fields format is not valid',
        'max_length': 'max_length is 30 chars',
        'min_length': 'password should be at least 8 Chars',
        'password_mismatch' : ("The twoadadadada."),
        }



        
class MyAuthForm(AuthenticationForm):
    class Meta:
        model = Usuario
        fields = ['username','password']
    def __init__(self, *args, **kwargs):
        super(MyAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Username'})
        self.fields['username'].label = False
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder':'Password'}) 
        self.fields['password'].label = False



class AddProductForm(forms.Form):
    codigo_barras = forms.CharField(label='Código de Barras', max_length=20)
