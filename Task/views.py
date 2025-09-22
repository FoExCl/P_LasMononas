from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Empleados, AuthUser, AuthUserGroups, AuthUserUserPermissions, Ventas, Productos, Cajas
from .forms import EmpleadoCreationForm, EditarEmpleadoForm, EditarPerfilForm, CambiarContraseñaForm, ProductoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth,TruncWeek
from django.utils.translation import activate
from django.db.models import Count, Sum, F
import logging
import json

logger = logging.getLogger(__name__)


# ===== AUTENTICACIÓN =====
def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrecta'
            })
        login(request, user)
        return redirect('inicio')


@login_required
def exit(request):
    logout(request)
    return redirect('signin')


@login_required
def inicio(request):
    """
    Redirige a todos los usuarios a su perfil primero
    """
    return redirect('user_profile')


# ===== PERFIL DE USUARIO =====
@login_required
def user_profile(request):
    auth_user = get_object_or_404(AuthUser, username=request.user.username)
    empleado = get_object_or_404(Empleados, id_user=auth_user)
    edit_form = EditarPerfilForm(instance=empleado)
    password_form = CambiarContraseñaForm()
    return render(request, 'user.html', {
        'empleado': empleado,
        'edit_form': edit_form,
        'password_form': password_form
    })


@login_required
@require_http_methods(["POST"])
def change_password(request):
    form = CambiarContraseñaForm(request.POST)
    if form.is_valid():
        user = request.user
        if user.check_password(form.cleaned_data['password_actual']):
            user.set_password(form.cleaned_data['password_nueva'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
        else:
            messages.error(request, 'La contraseña actual es incorrecta.')
    else:
        messages.error(request, 'Errores en el formulario.')
    return redirect('user_profile')


@login_required
@require_http_methods(["POST"])
def edit_profile(request, user_id):
    """
    Edita el perfil propio o de otro usuario si eres administrador.
    """
    empleado = get_object_or_404(Empleados, id_user__id=user_id)

    # Empleado normal solo puede editar su perfil
    if not request.user.is_staff and str(request.user.id) != str(user_id):
        raise PermissionDenied("No puedes editar el perfil de otro usuario.")

    # No permitir que un empleado edite superadministradores
    if empleado.id_user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("No puedes editar un super administrador.")

    form_class = EditarPerfilForm if not request.user.is_staff else EditarEmpleadoForm
    form = form_class(request.POST or None, instance=empleado)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"Perfil de {empleado.nombre} actualizado correctamente.")
            return redirect('user_profile')
        else:
            messages.error(request, "Errores en el formulario.")

    return render(request, 'edit_user.html', {'form': form, 'empleado': empleado})


# ===== LISTA DE USUARIOS =====
@login_required
def user_list(request):
    """
    Solo administradores pueden ver la lista de usuarios.
    """
    if not request.user.is_staff:
        raise PermissionDenied("No tienes permiso para ver la lista de usuarios.")

    empleados = Empleados.objects.all().select_related('id_user')
    return render(request, 'userlist.html', {'empleados': empleados})


# ===== CREAR Y EDITAR USUARIOS =====
@login_required
@require_http_methods(["GET", "POST"])
def add_user(request):
    """
    Crear un nuevo usuario. Solo administradores pueden crear.
    """
    if not request.user.is_staff:
        raise PermissionDenied("No tienes permiso para crear usuarios.")

    if request.method == 'POST':
        form = EmpleadoCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"El usuario {new_user.nombre} ha sido creado correctamente.")
            return redirect('user_list')
        else:
            return render(request, 'add_user.html', {'form': form})
    form = EmpleadoCreationForm()
    return render(request, 'add_user.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def edit_user(request, user_id):
    """
    Edita un usuario. Administradores pueden editar cualquier usuario, empleados solo su propio perfil.
    """
    empleado = get_object_or_404(Empleados, id_user__id=user_id)

    # Empleados normales solo pueden editar su perfil
    if not request.user.is_staff and str(request.user.id) != str(user_id):
        raise PermissionDenied("No puedes editar el perfil de otro usuario.")

    form_class = EditarPerfilForm if not request.user.is_staff else EditarEmpleadoForm
    form = form_class(request.POST or None, instance=empleado)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"Perfil de {empleado.nombre} actualizado correctamente.")
            return redirect('user_list' if request.user.is_staff else 'user_profile')
        else:
            messages.error(request, "Errores en el formulario.")

    return render(request, 'edit_user.html', {'form': form, 'empleado': empleado})


# ===== ACTIVAR/DESACTIVAR USUARIOS =====
@login_required
@require_http_methods(["POST"])
def toggle_user_active(request, user_id):
    if not request.user.is_staff:
        raise PermissionDenied("No tienes permiso para cambiar estado de usuarios.")

    empleado = get_object_or_404(Empleados, id_user__id=user_id)
    user = empleado.id_user

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "No puedes cambiar el estado de un super administrador.")
        return redirect('user_list')

    user.is_active = not user.is_active
    user.save()
    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f"El usuario {empleado.nombre} ha sido {status}.")
    return redirect('user_list')


# ===== RESETEO DE CONTRASEÑA =====
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        logger.info("Formulario válido, guardando nueva contraseña")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.error(f"Formulario inválido: {form.errors}")
        return super().form_invalid(form)

# ===== VISTAS PARA GESTIÓN DE PRODUCTOS Y STOCK =====

@login_required
def lista_productos(request):
    """Lista todos los productos con alertas de stock bajo"""
    productos = Productos.objects.all().order_by('nombre_producto')
    productos_bajo_stock = productos.filter(stock__lte=F('stock_minimo'))
    productos_sin_stock = productos.filter(stock=0)
    
    context = {
        'productos': productos,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_sin_stock': productos_sin_stock,
        'alertas_count': productos_bajo_stock.count(),
    }
    return render(request, 'productos/lista.html', context)

@login_required
def crear_producto(request):
    """Crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre_producto}" creado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al crear el producto. Verifica los datos.')
    else:
        form = ProductoForm()
    
    return render(request, 'productos/form.html', {'form': form, 'title': 'Nuevo Producto'})

@login_required
def editar_producto(request, producto_id):
    """Editar un producto existente"""
    producto = get_object_or_404(Productos, id_producto=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto_editado = form.save()
            messages.success(request, f'Producto "{producto_editado.nombre_producto}" actualizado exitosamente.')
            
            # Verificar si el stock está bajo después de la edición
            if producto_editado.necesita_restock:
                messages.warning(request, f'¡ALERTA! El producto "{producto_editado.nombre_producto}" tiene stock bajo ({producto_editado.stock} unidades).')
            
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al actualizar el producto. Verifica los datos.')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'productos/form.html', {
        'form': form, 
        'title': f'Editar Producto: {producto.nombre_producto}',
        'producto': producto
    })

@login_required
def eliminar_producto(request, producto_id):
    """Eliminar un producto"""
    producto = get_object_or_404(Productos, id_producto=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre_producto
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('lista_productos')
    
    return render(request, 'productos/eliminar.html', {'producto': producto})

@login_required
def dashboard_stock(request):
    """Dashboard con alertas de stock y estadísticas"""
    
    productos_total = Productos.objects.count()
    productos_bajo_stock = Productos.objects.filter(stock__lte=F('stock_minimo'))
    productos_sin_stock = Productos.objects.filter(stock=0)
    productos_stock_normal = Productos.objects.filter(stock__gt=F('stock_minimo'))
    
    # Productos que más necesitan restock (ordenados por diferencia entre stock y stock_minimo)
    productos_criticos = productos_bajo_stock.extra(
        select={'diferencia': 'stock_minimo - stock'}
    ).order_by('-diferencia')[:5]
    
    context = {
        'productos_total': productos_total,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_normal': productos_stock_normal,
        'productos_criticos': productos_criticos,
        'alertas_count': productos_bajo_stock.count(),
        'sin_stock_count': productos_sin_stock.count(),
    }
    
    return render(request, 'productos/dashboard.html', context)