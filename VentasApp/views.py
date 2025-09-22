from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from Task.models import TurnosCaja, Productos, Ventas, DetallesVenta
from .forms import Ventasform, DetalleVentaFormSet
from django.db import transaction

@login_required
def lista_ventas(request):
    ventas = Ventas.objects.all()
    return render(request, 'ventas/lista.html', {'ventas': ventas})

@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def crear_venta(request):
    turnos_abiertos = TurnosCaja.objects.filter(fecha_cierre__isnull=True)
    if not turnos_abiertos.exists():
        messages.warning(request, 'No hay cajas abiertas. Abre un turno antes de vender.')
        return redirect('lista_ventas')

    # No fijamos fecha_venta aquí; el modelo Ventas ya tiene default
    venta = Ventas(total_venta=0)

    if request.method == 'POST':
        form = Ventasform(request.POST, instance=venta)
        form.fields['id_turno'].queryset = turnos_abiertos
        formset = DetalleVentaFormSet(request.POST, instance=venta)

        if form.is_valid() and formset.is_valid():
            # Guardar venta primero para obtener id
            venta = form.save(commit=False)
            venta.save()

            detalles = formset.save(commit=False)

            # 1) Validar stock para todos los detalles antes de tocar nada
            for detalle in detalles:
                # detalle.id_producto_id obtiene el PK del producto (sin resolver la relación)
                prod_pk = detalle.id_producto_id
                try:
                    producto = Productos.objects.select_for_update().get(pk=prod_pk)
                except Productos.DoesNotExist:
                    messages.error(request, f"El producto (id={prod_pk}) no existe.")
                    transaction.set_rollback(True)
                    return redirect('crear_venta')

                if producto.stock is None:
                    messages.error(request, f"Stock no definido para {producto.nombre_producto}.")
                    transaction.set_rollback(True)
                    return redirect('crear_venta')

                if producto.stock < detalle.cantidad:
                    messages.error(
                        request,
                        f"Stock insuficiente para {producto.nombre_producto} (Disponible: {producto.stock})"
                    )
                    transaction.set_rollback(True)
                    return redirect('crear_venta')

            # 2) Si todo ok, guardar cada detalle y descontar stock
            total = 0
            for detalle in detalles:
                producto = Productos.objects.select_for_update().get(pk=detalle.id_producto_id)

                detalle.id_venta = venta
                detalle.subtotal = producto.precio * detalle.cantidad  # usa 'precio' según tu modelo
                detalle.save()

                # descontar stock y guardar producto
                producto.stock -= detalle.cantidad
                producto.save()

                total += detalle.subtotal

            # 3) actualizar total de la venta y redirigir
            venta.total_venta = total - (venta.descuento or 0)
            venta.save()

            messages.success(request, f'Venta registrada ✅ Total: ${venta.total_venta:.2f}')
            return redirect('lista_ventas')
    else:
        form = Ventasform(instance=venta)
        form.fields['id_turno'].queryset = turnos_abiertos
        formset = DetalleVentaFormSet(instance=venta)

    productos = Productos.objects.all()
    return render(request, 'ventas/form.html', {
        'form': form,
        'formset': formset,
        'productos': productos
    })
    
@login_required
def editar_venta(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied("Solo los administradores pueden editar ventas.")
    venta = get_object_or_404(Ventas, pk=pk)
    if request.method == 'POST':
        form = Ventasform(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venta actualizada correctamente.')
            return redirect('lista_ventas')
    else:
        form = Ventasform(instance=venta)
    return render(request, 'ventas/form.html', {'form': form})

@login_required
def eliminar_venta(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied("Solo los administradores pueden eliminar ventas.")
    venta = get_object_or_404(Ventas, pk=pk)
    if request.method == 'POST':
        venta.delete()
        messages.success(request, 'Venta eliminada correctamente.')
        return redirect('lista_ventas')
    return render(request, 'ventas/eliminar.html', {'venta': venta})
