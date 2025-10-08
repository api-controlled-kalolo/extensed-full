from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from ventas.forms import ClienteForm
from ventas.models import Cliente
from ventas.utils.ubigeo import get_district_choices, is_valid_province_value
from ventas.utils.excel import build_workbook, workbook_to_response


def cliente_dashboard(request):
    """Dashboard principal de gestión de clientes"""
    context = {
        'cliente_count': Cliente.objects.count(),
    }
    return render(request, 'clientes/cliente_dashboard.html', context)


def crear_cliente(request):
    if request.method == 'GET':
        return render(request, 'clientes/crear_clientes.html', {
            'form': ClienteForm()
        })

    form = ClienteForm(request.POST)
    if form.is_valid():
        new_cliente = form.save()
        messages.success(request, 'Cliente creado correctamente.')
        return redirect('ventas:cliente_dashboard')

    return render(request, 'clientes/crear_clientes.html', {'form': form})


def listar_clientes(request):
    """Vista de listado de clientes con búsqueda"""
    clientes = Cliente.objects.select_related('proyecto_principal__unidad_negocio_principal').order_by('razon_social')
    context = {
        'clientes': clientes,
    }
    return render(request, 'clientes/listar_clientes.html', context)


def buscar_clientes_json(request):
    """Endpoint JSON para búsqueda en tiempo real"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        clientes = Cliente.objects.select_related('proyecto_principal__unidad_negocio_principal').order_by('razon_social')[:50]
    else:
        clientes = Cliente.objects.select_related(
            'proyecto_principal__unidad_negocio_principal'
        ).filter(
            Q(codigo__icontains=query) |
            Q(ruc__icontains=query) |
            Q(razon_social__icontains=query) |
            Q(direccion__icontains=query) |
            Q(distrito__icontains=query) |
            Q(provincia__icontains=query)
        ).order_by('razon_social')[:50]
    
    data = [{
        'id': c.id,
        'codigo': c.codigo,
        'ruc': c.ruc,
        'razon_social': c.razon_social,
        'direccion': c.direccion,
        'distrito': c.distrito,
        'provincia': c.provincia,
        'proyecto': c.proyecto_principal.nombre if c.proyecto_principal else 'N/A',
    } for c in clientes]
    
    return JsonResponse({'clientes': data})


def distritos_por_provincia(request):
    """Devuelve los distritos asociados a la provincia seleccionada."""

    province_value = request.GET.get('provincia', '').strip()
    if not is_valid_province_value(province_value):
        return JsonResponse({'distritos': []})

    district_choices = get_district_choices(province_value)
    distritos = [{'value': value, 'label': label} for value, label in district_choices]
    return JsonResponse({'distritos': distritos})


def editar_cliente(request, cliente_id):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'GET':
        form = ClienteForm(instance=cliente)
        return render(request, 'clientes/editar_cliente.html', {
            'form': form,
            'cliente': cliente,
        })
    
    form = ClienteForm(request.POST, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, f'Cliente "{cliente.razon_social}" actualizado correctamente.')
        return redirect('ventas:listar_clientes')
    
    return render(request, 'clientes/editar_cliente.html', {
        'form': form,
        'cliente': cliente,
    })


def eliminar_cliente(request, cliente_id):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        razon = cliente.razon_social
        cliente.delete()
        messages.success(request, f'Cliente "{razon}" eliminado correctamente.')
        return redirect('ventas:listar_clientes')
    
    return render(request, 'clientes/confirmar_eliminar.html', {'cliente': cliente})


def exportar_clientes_excel(request):
    clientes = Cliente.objects.select_related(
        'proyecto_principal__unidad_negocio_principal'
    ).order_by('razon_social')

    headers = [
        'Código',
        'RUC',
        'Razón Social',
        'Dirección',
        'Distrito',
        'Provincia',
        'Proyecto',
        'Unidad de Negocio',
    ]

    rows = []
    for cliente in clientes:
        proyecto = cliente.proyecto_principal
        unidad = proyecto.unidad_negocio_principal if proyecto else None
        rows.append([
            cliente.codigo or '',
            cliente.ruc,
            cliente.razon_social,
            cliente.direccion,
            cliente.distrito,
            cliente.provincia,
            proyecto.nombre if proyecto else '',
            unidad.nombre if unidad else '',
        ])

    workbook = build_workbook('Clientes', headers, rows)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return workbook_to_response(workbook, f'clientes_{timestamp}.xlsx')
