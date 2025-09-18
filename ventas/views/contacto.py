from django.shortcuts import render, redirect
from django.contrib import messages
from ventas.forms import ContactoForm

def crear_contacto(request):
    # GET: mostrar el formulario
    if request.method == 'GET':
        return render(request, 'contacto/crear_contactos.html', {'form': ContactoForm()})

    # POST: procesar envío
    form = ContactoForm(request.POST)
    if form.is_valid():
        new_contacto = form.save()
        messages.success(request, 'Contacto creado correctamente.')
        return redirect(request.path)

    # Si no es válido, re-renderizar con errores
    return render(request, 'contacto/crear_contactos.html', {'form': form})