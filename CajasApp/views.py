from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from Task.models import Cajas, TurnosCaja, Empleados, AuthUser
from .forms import CajaForm, TurnoForm


@login_required
@require_http_methods(["GET", "POST"])
def lista_cajas(request):
    cajas = Cajas.objects.all()
    return render(request, 'cajas/lista.html', {'cajas': cajas})


@login_required
@require_http_methods(["GET", "POST"])
def crear_caja(request):
    if request.method == 'POST':
        form = CajaForm(request.POST)
        if form.is_valid():
            ubicacion = form.cleaned_data['ubicacion']

            if Cajas.objects.filter(ubicacion=ubicacion, estado='Abierta').exists():
                form.add_error(None, 'Ya existe una caja abierta en esta ubicación; ciérrala antes de abrir otra.')
            else:
                caja = form.save(commit=False)

                if ubicacion == "Monona, zn oeste":
                    caja.id_sucursal_id = 1
                elif ubicacion == "Monona, zn norte":
                    caja.id_sucursal_id = 2
                else:
                    caja.id_sucursal = None

                caja.estado = 'Abierta'
                caja.save()

                # === Aquí resolvemos el problema del AuthUser ===
                auth_user = AuthUser.objects.get(username=request.user.username)

                try:
                    empleado = Empleados.objects.get(id_user=auth_user)
                except Empleados.DoesNotExist:
                    empleado = Empleados.objects.create(
                        nombre=request.user.first_name or request.user.username,
                        apellido=request.user.last_name or '',
                        correo=request.user.email or '',
                        id_user=auth_user
                    )

                TurnosCaja.objects.create(
                    id_caja=caja,
                    id_empleado=empleado,
                    fecha_apertura=timezone.now()
                )

                messages.success(request, 'Caja y turno creados correctamente ✅')
                return redirect('lista_cajas')
    else:
        form = CajaForm()

    return render(request, 'cajas/form.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def editar_caja(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        form = CajaForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save(commit=False)

            ubicacion = form.cleaned_data.get('ubicacion')
            if ubicacion == "Monona, zn oeste":
                caja.id_sucursal_id = 1
            elif ubicacion == "Monona, zn norte":
                caja.id_sucursal_id = 2

            caja.save()
            return redirect('lista_cajas')
    else:
        form = CajaForm(instance=caja)
    return render(request, 'cajas/form.html', {'form': form})


@login_required
@require_http_methods(["GET", "POST"])
def eliminar_caja(request, pk):
    caja = get_object_or_404(Cajas, pk=pk)
    if request.method == 'POST':
        caja.delete()
        return redirect('lista_cajas')
    return render(request, 'cajas/eliminar.html', {'caja': caja})
