from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import ModelForm, fields, Form
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


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


def validate_multiplo_10(value):
    if value % 10 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $10')

def validate_multiplo_50(value):
    if value % 50 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $50')

def validate_multiplo_100(value):
    if value % 100 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $100')

def validate_multiplo_500(value):
    if value % 500 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $500')

def validate_multiplo_1000(value):
    if value % 1000 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $1000')

def validate_multiplo_2000(value):
    if value % 2000 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $2000')

def validate_multiplo_5000(value):
    if value % 5000 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $5000')

def validate_multiplo_10000(value):
    if value % 10000 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $10000')

def validate_multiplo_20000(value):
    if value % 20000 != 0:
        raise ValidationError('El valor debe ser un múltiplo de $20000')


class BilletesMonedasForm(forms.Form):
    monedas_10 = forms.IntegerField(
        label='Monedas de $10',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_10,
        ]
    )
    monedas_50 = forms.IntegerField(
        label='Monedas de $50',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_50,
        ]
    )
    monedas_100 = forms.IntegerField(
        label='Monedas de $100',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_100,
        ]
    )
    monedas_500 = forms.IntegerField(
        label='Monedas de $500',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_500,
        ]
    )
    billetes_1000 = forms.IntegerField(
        label='Billetes de $1000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_1000,
        ]
    )
    billetes_2000 = forms.IntegerField(
        label='Billetes de $2000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_2000,
        ]
    )
    billetes_5000 = forms.IntegerField(
        label='Billetes de $5000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_5000,
        ]
    )
    billetes_10000 = forms.IntegerField(
        label='Billetes de $10000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_10000,
        ]
    )
    billetes_20000 = forms.IntegerField(
        label='Billetes de $20000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_20000,
        ]
    )
    maquinas_debito = forms.IntegerField(label='Monto de máquinas de débito', initial=0)



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
    clave_anulacion = forms.CharField(max_length=20, required=True, label="Clave de anulación")

    class Meta:
        model = GastoCaja
        fields = ['monto', 'descripcion']

    def clean(self):
        cleaned_data = super().clean()
        clave_anulacion = cleaned_data.get('clave_anulacion')
        
        # Realiza cualquier validación adicional que necesites para la clave de anulación aquí

        return cleaned_data