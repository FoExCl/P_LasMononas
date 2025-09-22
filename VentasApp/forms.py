from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit
from Task.models import Ventas, DetallesVenta, Productos

class Ventasform(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = ['id_turno', 'nombre_cliente', 'total_venta', 'metodo_pago', 'descuento', 'vuelto']
        widgets = {
            'total_venta': forms.NumberInput(attrs={'step': '0.01', 'readonly': 'readonly'}),
            'nombre_cliente': forms.TextInput(attrs={'placeholder': 'Nombre del cliente'}),
            'descuento': forms.NumberInput(attrs={'step': '0.01'}),
            'vuelto': forms.NumberInput(attrs={'step': '0.01', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('id_turno', css_class='form-select'),
                Field('nombre_cliente', css_class='form-control'),
                Field('total_venta', css_class='form-control'),
                Field('descuento', css_class='form-control'),
                Field('vuelto', css_class='form-control'),
                Field('metodo_pago', css_class='form-select'),
            ),
            Submit('submit', '💾 Guardar Venta', css_class='btn btn-primary')
        )

DetalleVentaFormSet = inlineformset_factory(
    Ventas, DetallesVenta,
    fields=['id_producto', 'cantidad'],
    extra=1,
    can_delete=True,
    widgets={
        'cantidad': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        'id_producto': forms.Select(attrs={'class': 'form-select'})
    }
)
