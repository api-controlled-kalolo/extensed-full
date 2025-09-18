from django.shortcuts import render, redirect
from django.contrib import messages
from ventas.forms import UnidadNegocioForm


def crear_unidad_negocio(request):
    # GET: mostrar el formulario
    if request.method == 'GET':
        return render(request, 'unidad_negocio/create_un.html', {
            'form': UnidadNegocioForm()
        })

    # POST: procesar envío
    form = UnidadNegocioForm(request.POST)
    if form.is_valid():
        new_un = form.save()
        messages.success(request, 'Unidad de negocio creada correctamente.')
        # Redirigir al mismo formulario (evita reenvío al refrescar)
        return redirect(request.path)

    # Si no es válido, re-renderizar con errores
    return render(request, 'unidad_negocio/create_un.html', {'form': form})