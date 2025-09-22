# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Cajas(models.Model):
    id_caja = models.AutoField(primary_key=True)
    id_sucursal = models.ForeignKey('Sucursales', models.DO_NOTHING, db_column='id_sucursal')
    ubicacion = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cajas'


class DetallesVenta(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey('Ventas', on_delete=models.CASCADE, db_column='id_venta', null=True, blank=True)
    id_producto = models.ForeignKey('Productos', on_delete=models.DO_NOTHING, db_column='id_producto', null=True, blank=True)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalles_venta'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Empleados(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_user')
    edad = models.IntegerField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    correo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'empleados'


class Gastos(models.Model):
    id_gasto = models.AutoField(primary_key=True)
    id_turno = models.ForeignKey('TurnosCaja', models.DO_NOTHING, db_column='id_turno')
    fecha_gasto = models.DateTimeField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gastos'


class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    stock_minimo = models.IntegerField(default=5, help_text='Stock mínimo antes de mostrar alerta')

    class Meta:
        managed = True
        db_table = 'productos'

    def __str__(self):
        return self.nombre_producto

    @property
    def necesita_restock(self):
        return self.stock <= self.stock_minimo

    @property
    def estado_stock(self):
        if self.stock <= 0:
            return 'sin_stock'
        elif self.stock <= self.stock_minimo:
            return 'stock_bajo'
        return 'stock_normal'


class Sucursales(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sucursales'


class TurnosCaja(models.Model):
    id_turno = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='id_caja')
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    fecha_apertura = models.DateTimeField()
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    egresos_totales = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'turnos_caja'

class Ventas(models.Model):
    METODO_PAGO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
        ('QR', 'QR'),
    ]
    
    id_venta = models.AutoField(primary_key=True)
    id_turno = models.ForeignKey(
        'TurnosCaja', 
        on_delete=models.CASCADE, 
        db_column='id_turno', 
        null=True, 
        blank=True
    )
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    fecha_venta = models.DateTimeField(default=timezone.now)  # Se asigna automáticamente al crear
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='Efectivo')
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        managed = True
        db_table = 'ventas'

    def __str__(self):
        return f"Venta #{self.id_venta} - Total: {self.total_venta}"