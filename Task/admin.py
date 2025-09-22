from django.contrib import admin
from .models import Empleados, Productos, Sucursales, Cajas, TurnosCaja, Ventas, DetallesVenta, Gastos

@admin.register(Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ['id_empleado', 'nombre', 'apellido', 'correo', 'telefono']
    search_fields = ['nombre', 'apellido', 'correo']

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'nombre_producto', 'precio', 'stock']
    search_fields = ['nombre_producto']

@admin.register(Sucursales)
class SucursalesAdmin(admin.ModelAdmin):
    list_display = ['id_sucursal', 'nombre_sucursal', 'direccion']

@admin.register(Cajas)
class CajasAdmin(admin.ModelAdmin):
    list_display = ['id_caja', 'id_sucursal', 'ubicacion', 'estado']

@admin.register(TurnosCaja)
class TurnosCajaAdmin(admin.ModelAdmin):
    list_display = ['id_turno', 'id_empleado', 'fecha_apertura', 'fecha_cierre']

@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'nombre_cliente', 'fecha_venta', 'total_venta']

@admin.register(DetallesVenta)
class DetallesVentaAdmin(admin.ModelAdmin):
    list_display = ['id_detalle', 'id_venta', 'id_producto', 'cantidad', 'subtotal']

@admin.register(Gastos)
class GastosAdmin(admin.ModelAdmin):
    list_display = ['id_gasto', 'id_turno', 'fecha_gasto', 'monto', 'concepto']