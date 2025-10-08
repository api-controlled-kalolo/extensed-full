from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from ventas.forms import ProyectoForm
from ventas.models import Proyecto, UnidadNegocio
from ventas.utils.excel import build_workbook, workbook_to_response


def crear_proyecto(request):
    form = ProyectoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        proyecto = form.save()
        messages.success(
            request,
            f"Se creó el proyecto “{proyecto.nombre}” correctamente."
        )
        return redirect(reverse('ventas:proyecto_list'))

    return render(request, 'proyecto/crear_proyecto.html', {'form': form})


def listar_proyectos(request):
    search = (request.GET.get('q') or '').strip()
    unidad_id = (request.GET.get('unidad') or '').strip()

    proyectos = (
        Proyecto.objects
        .select_related('unidad_negocio_principal')
        .annotate(total_clientes=Count('clientes', distinct=True))
    )

    if search:
        proyectos = proyectos.filter(
            Q(nombre__icontains=search)
            | Q(codigo__icontains=search)
            | Q(unidad_negocio_principal__nombre__icontains=search)
            | Q(unidad_negocio_principal__codigo__icontains=search)
        )

    if unidad_id:
        proyectos = proyectos.filter(unidad_negocio_principal_id=unidad_id)

    proyectos = proyectos.order_by('nombre')

    unidades = UnidadNegocio.objects.all().order_by('nombre')

    return render(request, 'proyecto/list_proyecto.html', {
        'proyectos': proyectos,
        'q': search,
        'unidad_id': unidad_id,
        'unidades': unidades,
    })


def editar_proyecto(request, pk: int):
    proyecto = get_object_or_404(
        Proyecto.objects.select_related('unidad_negocio_principal'),
        pk=pk
    )
    form = ProyectoForm(request.POST or None, instance=proyecto)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            f"El proyecto “{proyecto.nombre}” se actualizó correctamente."
        )
        return redirect(reverse('ventas:proyecto_list'))

    return render(request, 'proyecto/edit_proyecto.html', {
        'form': form,
        'proyecto': proyecto,
    })


def eliminar_proyecto(request, pk: int):
    proyecto = get_object_or_404(
        Proyecto.objects.select_related('unidad_negocio_principal'),
        pk=pk
    )
    clientes_count = proyecto.clientes.count()

    if request.method == 'POST':
        if clientes_count:
            messages.error(
                request,
                'No puedes eliminar el proyecto porque tiene clientes asociados. '
                'Reasigna o elimina primero esos clientes.'
            )
            return redirect(reverse('ventas:proyecto_list'))

        nombre = proyecto.nombre
        proyecto.delete()
        messages.success(
            request,
            f"El proyecto “{nombre}” se eliminó correctamente."
        )
        return redirect(reverse('ventas:proyecto_list'))

    return render(request, 'proyecto/confirm_delete_proyecto.html', {
        'proyecto': proyecto,
        'bloqueado': bool(clientes_count),
        'total_clientes': clientes_count,
    })


def exportar_proyectos_excel(request):
    proyectos = Proyecto.objects.select_related('unidad_negocio_principal').annotate(
        total_clientes=Count('clientes', distinct=True)
    ).order_by('nombre')

    headers = [
        'Código',
        'Nombre',
        'Unidad de Negocio',
        'Clientes Asociados',
    ]

    rows = []
    for proyecto in proyectos:
        unidad = proyecto.unidad_negocio_principal
        rows.append([
            proyecto.codigo or '',
            proyecto.nombre,
            f"{unidad.codigo} · {unidad.nombre}" if unidad else '',
            proyecto.total_clientes,
        ])

    workbook = build_workbook('Proyectos', headers, rows)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return workbook_to_response(workbook, f'proyectos_{timestamp}.xlsx')
