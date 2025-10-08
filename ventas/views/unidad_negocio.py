from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ventas.forms import UnidadNegocioForm
from ventas.models import UnidadNegocio


def crear_unidad_negocio(request):
    form = UnidadNegocioForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        unidad = form.save()
        messages.success(
            request,
            f"Se creó la Unidad de Negocio “{unidad.nombre}” correctamente."
        )
        return redirect(reverse('ventas:unidadnegocio_list'))

    return render(request, 'unidad_negocio/create_un.html', {'form': form})


def listar_unidades_negocio(request):
    unidades = (
        UnidadNegocio.objects
        .annotate(total_proyectos=Count('unidad_negocio', distinct=True))
        .order_by('nombre')
    )

    return render(request, 'unidad_negocio/list_un.html', {
        'unidades': unidades,
    })


def editar_unidad_negocio(request, pk: int):
    unidad = get_object_or_404(UnidadNegocio, pk=pk)
    form = UnidadNegocioForm(request.POST or None, instance=unidad)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            f"La Unidad de Negocio “{unidad.nombre}” se actualizó correctamente."
        )
        return redirect(reverse('ventas:unidadnegocio_list'))

    return render(request, 'unidad_negocio/edit_un.html', {
        'form': form,
        'unidad': unidad,
    })


def eliminar_unidad_negocio(request, pk: int):
    unidad = get_object_or_404(UnidadNegocio, pk=pk)
    proyectos_count = unidad.unidad_negocio.count()

    if request.method == 'POST':
        if proyectos_count:
            messages.error(
                request,
                'No puedes eliminar la UN porque tiene proyectos asociados. '
                'Reasigna o elimina primero esos proyectos.'
            )
            return redirect(reverse('ventas:unidadnegocio_list'))

        unidad.delete()
        messages.success(
            request,
            f"La Unidad de Negocio “{unidad.nombre}” se eliminó correctamente."
        )
        return redirect(reverse('ventas:unidadnegocio_list'))

    return render(request, 'unidad_negocio/confirm_delete_un.html', {
        'unidad': unidad,
        'bloqueada': bool(proyectos_count),
        'total_proyectos': proyectos_count,
    })