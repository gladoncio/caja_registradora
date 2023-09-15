from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import ModelForm, fields, Form
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput


class UsuarioCreationForm(UserCreationForm):
    permisos = forms.ChoiceField(
        choices=[('admin', 'Admin'), ('cajero', 'Cajero')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'password1', 'password2', 'permisos', 'rut', 'clave_anulacion')

        
class MyAuthForm(AuthenticationForm):
    class Meta:
        model = Usuario
        fields = ['username','password']
    def __init__(self, *args, **kwargs):
        super(MyAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control form-control-lg resize-text', 'placeholder': 'Username'})
        self.fields['username'].label = False
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg resize-text', 'placeholder':'Password'}) 
        self.fields['password'].label = False



class AddProductForm(forms.Form):
    codigo_barras = forms.CharField(label='Código de Barras', max_length=20)


class CajaDiariaForm(forms.ModelForm):
    class Meta:
        model = CajaDiaria
        fields = ['monto', 'retiro']  # Lista los campos que deseas editar en el formulario



class BilletesMonedasForm(forms.Form):
    monedas_10 = forms.IntegerField(label='Monedas de $10', initial=0)
    monedas_50 = forms.IntegerField(label='Monedas de $50', initial=0)
    monedas_100 = forms.IntegerField(label='Monedas de $100', initial=0)
    monedas_500 = forms.IntegerField(label='Monedas de $500', initial=0)
    billetes_1000 = forms.IntegerField(label='Billetes de $1000', initial=0)
    billetes_2000 = forms.IntegerField(label='Billetes de $2000', initial=0)
    billetes_5000 = forms.IntegerField(label='Billetes de $5000', initial=0)
    billetes_10000 = forms.IntegerField(label='Billetes de $10000', initial=0)
    billetes_20000 = forms.IntegerField(label='Billetes de $20000', initial=0)


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplicar clases de Bootstrap a los widgets
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control resize-text'  # Clase Bootstrap para campos de formulario



class ContraseñaForm(forms.Form):
    contraseña = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control resize-text'})
    )


class BarcodeForm(forms.Form):
    barcode = forms.CharField(
        max_length=100,
        label='Código de Barras',
        widget=forms.TextInput(attrs={'class': 'form-control resize-text'})
    )

class GastoCajaForm(forms.ModelForm):
    class Meta:
        model = GastoCaja
        fields = ['monto', 'descripcion', 'registro_gastos']