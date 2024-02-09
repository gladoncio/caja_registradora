from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.forms import ModelForm, fields, Form
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import UserChangeForm

class UsuarioCreationForm(UserCreationForm):
    permisos = forms.ChoiceField(
        choices=Usuario.PERMISOS_CHOICES,  # Utiliza las opciones definidas en el modelo
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'password1', 'password2', 'permisos', 'rut', 'clave_anulacion')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a los campos
        self.fields['username'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['rut'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['clave_anulacion'].widget = forms.PasswordInput(attrs={'class': 'form-control resize-text onlyinput'})
        self.fields['permisos'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})


        
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
        fields = ['monto', 'retiro']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'retiro': forms.NumberInput(attrs={'class': 'form-control resize-text onlyinput'}),
        }

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
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    monedas_50 = forms.IntegerField(
        label='Monedas de $50',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_50,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    monedas_100 = forms.IntegerField(
        label='Monedas de $100',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_100,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    monedas_500 = forms.IntegerField(
        label='Monedas de $500',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_500,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    billetes_1000 = forms.IntegerField(
        label='Billetes de $1000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_1000,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    billetes_2000 = forms.IntegerField(
        label='Billetes de $2000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_2000,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    billetes_5000 = forms.IntegerField(
        label='Billetes de $5000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_5000,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    billetes_10000 = forms.IntegerField(
        label='Billetes de $10000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_10000,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    billetes_20000 = forms.IntegerField(
        label='Billetes de $20000',
        initial=0,
        validators=[
            MinValueValidator(0),
            validate_multiplo_20000,
        ],
        widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'})
    )
    maquinas_debito = forms.IntegerField(label='Monto de máquinas de débito', initial=0,widget=forms.TextInput(attrs={'class': 'form-control onlyinput resize-text'}))



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
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control resize-text onlyinput'})
    )


class BarcodeForm(forms.Form):
    barcode = forms.CharField(
        max_length=100,
        label='Código de Barras',
        widget=forms.TextInput(attrs={'class': 'form-control resize-text'})
    )
    cantidad = forms.IntegerField(label='Cantidad', initial=1, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control resize-text onlyinput'}))

class GastoCajaForm(forms.ModelForm):
    clave_anulacion = forms.CharField(
        max_length=20,
        required=True,
        label="Clave Personal",
        widget=forms.PasswordInput(attrs={'class': 'form-control resize-text onlyinput'}),
    )

    class Meta:
        model = GastoCaja
        fields = ['monto', 'descripcion']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control resize-text onlyinput'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        clave_anulacion = cleaned_data.get('clave_anulacion')
        
        # Realiza cualquier validación adicional que necesites para la clave de anulación aquí

        return cleaned_data
    

class CambiarClaveForm(forms.Form):
    nueva_clave = forms.CharField(
        label='Nueva Clave',
        widget=forms.PasswordInput(attrs={'class': 'onlyinput resize-text form-control'})
    )
    confirmar_clave = forms.CharField(
        label='Confirmar Clave',
        widget=forms.PasswordInput(attrs={'class': 'onlyinput resize-text form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva_clave = cleaned_data.get('nueva_clave')
        confirmar_clave = cleaned_data.get('confirmar_clave')

        if nueva_clave and confirmar_clave:
            if nueva_clave != confirmar_clave:
                raise forms.ValidationError('Las claves no coinciden.')

        return cleaned_data

class ValorForm(forms.Form):
    valor = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control resize-text onlyinput'})
    )
class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('username', 'permisos', 'rut')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agregar clases de Bootstrap a los campos
        self.fields['username'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['permisos'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['rut'].widget.attrs.update({'class': 'form-control resize-text onlyinput'})
        self.fields['password'].widget = forms.HiddenInput()
class CambiarClaveAnulacionForm(forms.ModelForm):
    nueva_clave_anulacion = forms.CharField(
        label='Nueva Clave de Anulación',
        widget=forms.PasswordInput(attrs={'class': 'form-control resize-text onlyinput'}),
        max_length=20,
        required=False  # Puede ser opcional
    )

    class Meta:
        model = Usuario
        fields = ['nueva_clave_anulacion']


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'valor_costo', 'precio', 'codigo_barras', 'gramaje', 'foto', 'descripcion', 'departamento', 'marca', 'tipo_gramaje', 'tipo_venta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control onlyinput'}),
            'valor_costo': forms.NumberInput(attrs={'class': 'form-control onlyinput'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control onlyinput'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control onlyinput'}),
            'gramaje': forms.NumberInput(attrs={'class': 'form-control onlyinput'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control onlyinput'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control onlyinput'}),
            'departamento': forms.Select(attrs={'class': 'form-control onlyinput'}),
            'marca': forms.Select(attrs={'class': 'form-control onlyinput'}),
            'tipo_gramaje': forms.Select(attrs={'class': 'form-control onlyinput'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-control onlyinput'}),
        }

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['decimales', 'clave_anulacion', 'idioma', 'imprimir', 'tipo_venta', 'porcentaje_iva', 'tamano_letra','separador']
        widgets = {
            'decimales': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'clave_anulacion': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'idioma': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'imprimir': forms.Select(attrs={'class': 'form-control resize-text onlyinput'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-control resize-text onlyinput'}),
            'porcentaje_iva': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'tamano_letra': forms.TextInput(attrs={'class': 'form-control resize-text onlyinput'}),
            'separador': forms.Select(attrs={'class': 'form-control resize-text onlyinput'}),

        }
