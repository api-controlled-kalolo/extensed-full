from django.shortcuts import render, redirect
from django.contrib import messages
from ventas.forms import ClienteForm

def crear_cliente(request):
    # GET: mostrar el formulario
    if request.method == 'GET':
        return render(request, 'clientes/crear_clientes.html', {
            'form': ClienteForm()
        })

    # POST: procesar envío
    form = ClienteForm(request.POST)
    if form.is_valid():
        new_cliente = form.save()
        messages.success(request, 'Cliente creado correctamente.')
        # Redirigir al mismo formulario (evita reenvío al refrescar)
        return redirect(request.path)

    # Si no es válido, re-renderizar con errores
    return render(request, 'clientes/crear_clientes.html', {'form': form})
