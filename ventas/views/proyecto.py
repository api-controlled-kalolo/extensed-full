from django.shortcuts import render, redirect
from django.contrib import messages
from ventas.forms import ProyectoForm

def crear_proyecto(request):
    # GET: mostrar el formulario
    if request.method == 'GET':
        return render(request, 'proyecto/crear_proyecto.html', {
            'form': ProyectoForm()
        })

    # POST: procesar envío
    form = ProyectoForm(request.POST)
    if form.is_valid():
        new_proyect = form.save()
        messages.success(request, 'Proyecto creado correctamente.')
        # Redirigir al mismo formulario (evita reenvío al refrescar)
        return redirect(request.path)

    # Si no es válido, re-renderizar con errores
    return render(request, 'proyecto/crear_proyecto.html', {'form': form})
