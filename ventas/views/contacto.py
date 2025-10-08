from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from ventas.forms import ContactoForm
from ventas.models import Contacto
from ventas.utils.excel import build_workbook, workbook_to_response


def contacto_dashboard(request):
    """Dashboard principal de gestión de contactos"""
    context = {
        'contacto_count': Contacto.objects.count(),
    }
    return render(request, 'contacto/contacto_dashboard.html', context)


def crear_contacto(request):
    """Vista para crear un nuevo contacto"""
    if request.method == 'GET':
        return render(request, 'contacto/crear_contactos.html', {'form': ContactoForm()})

    form = ContactoForm(request.POST)
    if form.is_valid():
        new_contacto = form.save()
        messages.success(request, 'Contacto creado correctamente.')
        return redirect('ventas:contacto_dashboard')

    return render(request, 'contacto/crear_contactos.html', {'form': form})


def listar_contactos(request):
    """Vista de listado de contactos con búsqueda"""
    contactos = Contacto.objects.select_related(
        'cliente_principal__proyecto_principal__unidad_negocio_principal'
    ).order_by('apellidos', 'nombres')
    
    context = {
        'contactos': contactos,
    }
    return render(request, 'contacto/listar_contactos.html', context)


def buscar_contactos_json(request):
    """Endpoint JSON para búsqueda en tiempo real"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        contactos = Contacto.objects.select_related(
            'cliente_principal__proyecto_principal__unidad_negocio_principal'
        ).order_by('apellidos', 'nombres')[:50]
    else:
        contactos = Contacto.objects.select_related(
            'cliente_principal__proyecto_principal__unidad_negocio_principal'
        ).filter(
            Q(apellidos__icontains=query) |
            Q(nombres__icontains=query) |
            Q(cargo__icontains=query) |
            Q(correo__icontains=query) |
            Q(Celular__icontains=query) |
            Q(Sede__icontains=query) |
            Q(cliente_principal__razon_social__icontains=query)
        ).order_by('apellidos', 'nombres')[:50]
    
    data = [{
        'id': c.id,
        'apellidos': c.apellidos,
        'nombres': c.nombres,
        'cargo': c.cargo,
        'correo': c.correo,
        'celular': c.Celular,
        'sede': c.Sede,
        'cliente': c.cliente_principal.razon_social if c.cliente_principal else 'N/A',
    } for c in contactos]
    
    return JsonResponse({'contactos': data})


def editar_contacto(request, contacto_id):
    """Vista para editar un contacto existente"""
    contacto = get_object_or_404(Contacto, id=contacto_id)
    
    if request.method == 'GET':
        form = ContactoForm(instance=contacto)
        return render(request, 'contacto/editar_contacto.html', {
            'form': form,
            'contacto': contacto,
        })
    
    form = ContactoForm(request.POST, instance=contacto)
    if form.is_valid():
        form.save()
        messages.success(request, f'Contacto "{contacto.nombres} {contacto.apellidos}" actualizado correctamente.')
        return redirect('ventas:listar_contactos')
    
    return render(request, 'contacto/editar_contacto.html', {
        'form': form,
        'contacto': contacto,
    })


def eliminar_contacto(request, contacto_id):
    """Vista para eliminar un contacto"""
    contacto = get_object_or_404(Contacto, id=contacto_id)
    
    if request.method == 'POST':
        nombre_completo = f"{contacto.nombres} {contacto.apellidos}"
        contacto.delete()
        messages.success(request, f'Contacto "{nombre_completo}" eliminado correctamente.')
        return redirect('ventas:listar_contactos')
    
    return render(request, 'contacto/confirmar_eliminar_contacto.html', {'contacto': contacto})


def exportar_contactos_excel(request):
    contactos = Contacto.objects.select_related(
        'cliente_principal__proyecto_principal__unidad_negocio_principal'
    ).order_by('apellidos', 'nombres')

    headers = [
        'Apellidos',
        'Nombres',
        'Cargo',
        'Correo',
        'Celular',
        'Sede',
        'Cliente',
        'Proyecto',
        'Unidad de Negocio',
    ]

    rows = []
    for contacto in contactos:
        cliente = contacto.cliente_principal
        proyecto = cliente.proyecto_principal if cliente else None
        unidad = proyecto.unidad_negocio_principal if proyecto else None

        rows.append([
            contacto.apellidos,
            contacto.nombres,
            contacto.cargo,
            contacto.correo,
            contacto.Celular,
            contacto.Sede,
            cliente.razon_social if cliente else '',
            proyecto.nombre if proyecto else '',
            unidad.nombre if unidad else '',
        ])

    workbook = build_workbook('Contactos', headers, rows)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return workbook_to_response(workbook, f'contactos_{timestamp}.xlsx')