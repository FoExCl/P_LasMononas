from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Empleados, AuthUser, AuthGroup, AuthUserGroups, Productos
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field, Row, Column
from crispy_forms.bootstrap import FormActions

class EmpleadoCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Nombre de usuario")
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirmar contraseña")
    rol = forms.ChoiceField(
        choices=[('vendedor', 'Vendedor'), ('administrador', 'Administrador')],
        required=True,
        label="Rol"
    )

    class Meta:
        model = Empleados
        fields = ['nombre', 'apellido', 'edad', 'telefono', 'correo', 'direccion']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if AuthUser.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if AuthUser.objects.filter(email=correo).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True, creator=None):
        # Crear usuario AuthUser
        user = AuthUser.objects.create(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['correo'],
            first_name=self.cleaned_data['nombre'],
            last_name=self.cleaned_data['apellido'],
            is_active=True,
            is_staff=self.cleaned_data['rol'] == 'administrador',
            is_superuser=self.cleaned_data['rol'] == 'administrador',
            password=make_password(self.cleaned_data['password1']),
            date_joined=timezone.now()
        )

        # Crear empleado
        empleado = super().save(commit=False)
        empleado.id_user = user

        if commit:
            empleado.save()

        # Asignar grupo automáticamente
        group, _ = AuthGroup.objects.get_or_create(name=self.cleaned_data['rol'])
        AuthUserGroups.objects.create(user=user, group=group)

        return empleado

class EditarEmpleadoForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Nombre de usuario")
    rol = forms.ChoiceField(
        choices=[('vendedor', 'Vendedor'), ('administrador', 'Administrador')],
        required=True,
        label="Rol"
    )
    is_active = forms.BooleanField(required=False, label="Activo")

    class Meta:
        model = Empleados
        fields = ['nombre', 'apellido', 'edad', 'telefono', 'correo', 'direccion']  # sin id_empleado

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id_user:
            self.fields['username'].initial = self.instance.id_user.username
            self.fields['nombre'].initial = self.instance.id_user.first_name
            self.fields['apellido'].initial = self.instance.id_user.last_name
            self.fields['correo'].initial = self.instance.id_user.email
            self.fields['is_active'].initial = self.instance.id_user.is_active
            user_group = AuthUserGroups.objects.filter(user=self.instance.id_user).first()
            if user_group:
                self.fields['rol'].initial = user_group.group.name

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if AuthUser.objects.filter(email=correo).exclude(id=self.instance.id_user.id).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado por otro usuario.')
        return correo

    def save(self, commit=True):
        empleado = super().save(commit=False)
        user = empleado.id_user

        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['nombre']
        user.last_name = self.cleaned_data['apellido']
        user.email = self.cleaned_data['correo']
        user.is_active = self.cleaned_data['is_active']
        user.is_staff = (self.cleaned_data['rol'] == 'administrador')
        # Preserve existing is_superuser status - do not modify it

        if commit:
            user.save()
            empleado.save()

            # Actualizar grupo del usuario
            new_rol = self.cleaned_data['rol']
            current_user_group = AuthUserGroups.objects.filter(user=user).first()
            if current_user_group:
                current_user_group.delete()

            new_group, _ = AuthGroup.objects.get_or_create(name=new_rol)
            AuthUserGroups.objects.create(user=user, group=new_group)

        return empleado


class EditarPerfilForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Nombre de usuario")

    class Meta:
        model = Empleados
        fields = ['nombre', 'apellido', 'edad', 'telefono', 'correo', 'direccion']  # sin id_empleado

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id_user:
            self.fields['username'].initial = self.instance.id_user.username
            self.fields['nombre'].initial = self.instance.id_user.first_name
            self.fields['apellido'].initial = self.instance.id_user.last_name
            self.fields['correo'].initial = self.instance.id_user.email

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if AuthUser.objects.filter(email=correo).exclude(id=self.instance.id_user.id).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado por otro usuario.')
        return correo

    def save(self, commit=True):
        empleado = super().save(commit=False)
        user = empleado.id_user

        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['nombre']
        user.last_name = self.cleaned_data['apellido']
        user.email = self.cleaned_data['correo']

        if commit:
            user.save()
            empleado.save()

        return empleado


class CambiarContraseñaForm(forms.Form):
    password_actual = forms.CharField(widget=forms.PasswordInput, label="Contraseña actual")
    password_nueva = forms.CharField(widget=forms.PasswordInput, label="Nueva contraseña")
    password_confirmacion = forms.CharField(widget=forms.PasswordInput, label="Confirmar nueva contraseña")

    def clean(self):
        cleaned_data = super().clean()
        password_nueva = cleaned_data.get("password_nueva")
        password_confirmacion = cleaned_data.get("password_confirmacion")

        if password_nueva and password_confirmacion and password_nueva != password_confirmacion:
            raise forms.ValidationError("Las nuevas contraseñas no coinciden.")

        return cleaned_data


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['nombre_producto', 'descripcion', 'precio', 'stock', 'stock_minimo']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripción del producto', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'min': '1', 'value': '5'}),
        }
        labels = {
            'nombre_producto': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'precio',
            'stock': 'Stock Actual',
            'stock_minimo': 'Stock Mínimo (Alerta)',
        }
        help_texts = {
            'stock_minimo': 'Cuando el stock llegue a este número o menos, se mostrará una alerta',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(Field('nombre_producto', css_class='form-control'), css_class='col-md-8'),
                Column(Field('precio', css_class='form-control'), css_class='col-md-4'),
            ),
            Field('descripcion', css_class='form-control'),
            Row(
                Column(Field('stock', css_class='form-control'), css_class='col-md-6'),
                Column(Field('stock_minimo', css_class='form-control'), css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', '💾 Guardar Producto', css_class='btn btn-primary'),
            )
        )
