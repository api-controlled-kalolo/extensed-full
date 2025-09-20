"""
Ejemplo de uso del servicio BCR en views.py

Puedes usar estas funciones en tus vistas para:
1. Mostrar el tipo de cambio actual
2. Actualizar manualmente el tipo de cambio de una cotización
3. Verificar si la API está disponible
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from ventas.models import Cotizacion
from services.bcr_service import BCRService


def mostrar_tipo_cambio_actual(request):
    """
    Vista para mostrar el tipo de cambio actual del BCR
    """
    try:
        tipo_cambio = BCRService.obtener_tipo_cambio_actual(con_margen=True)
        tipo_cambio_sin_margen = BCRService.obtener_tipo_cambio_actual(con_margen=False)
        api_disponible = BCRService.verificar_conexion()
        
        context = {
            'tipo_cambio_con_margen': tipo_cambio,
            'tipo_cambio_sin_margen': tipo_cambio_sin_margen,
            'margen': BCRService.MARGEN_SEGURIDAD,
            'api_disponible': api_disponible,
        }
        
        return render(request, 'ventas/tipo_cambio.html', context)
        
    except Exception as e:
        messages.error(request, f'Error obteniendo tipo de cambio: {e}')
        return render(request, 'ventas/tipo_cambio.html', {'error': True})


def actualizar_tipo_cambio_cotizacion(request, cotizacion_id):
    """
    Vista AJAX para actualizar el tipo de cambio de una cotización específica
    """
    if request.method == 'POST':
        try:
            cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
            
            # Guardar tipo de cambio anterior para comparación
            tipo_cambio_anterior = cotizacion.tipo_cambio
            
            # Actualizar con nuevo tipo de cambio del BCR
            nuevo_tipo_cambio = cotizacion.actualizar_tipo_cambio()
            cotizacion.save(update_fields=['tipo_cambio'])
            
            return JsonResponse({
                'success': True,
                'tipo_cambio_anterior': str(tipo_cambio_anterior) if tipo_cambio_anterior else 'N/A',
                'nuevo_tipo_cambio': str(nuevo_tipo_cambio),
                'mensaje': f'Tipo de cambio actualizado: {nuevo_tipo_cambio}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def obtener_tipo_cambio_api(request):
    """
    Vista AJAX que retorna el tipo de cambio actual sin guardar nada
    """
    try:
        tipo_cambio = BCRService.obtener_tipo_cambio_actual(con_margen=True)
        api_disponible = BCRService.verificar_conexion()
        
        return JsonResponse({
            'success': True,
            'tipo_cambio': str(tipo_cambio),
            'api_disponible': api_disponible,
            'margen_incluido': True,
            'margen': str(BCRService.MARGEN_SEGURIDAD)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Ejemplo de template HTML para mostrar en el frontend
TEMPLATE_EJEMPLO = """
<!-- ventas/templates/ventas/tipo_cambio.html -->
<div class="card">
    <div class="card-header">
        <h5>Tipo de Cambio BCR</h5>
    </div>
    <div class="card-body">
        {% if not error %}
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Tipo de cambio (sin margen):</strong> S/ {{ tipo_cambio_sin_margen }}</p>
                    <p><strong>Tipo de cambio (con margen +{{ margen }}):</strong> S/ {{ tipo_cambio_con_margen }}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>API BCR:</strong> 
                        {% if api_disponible %}
                            <span class="badge badge-success">Disponible</span>
                        {% else %}
                            <span class="badge badge-warning">No disponible</span>
                        {% endif %}
                    </p>
                </div>
            </div>
            
            <button id="actualizar-tipo-cambio" class="btn btn-primary">
                Actualizar Tipo de Cambio
            </button>
        {% else %}
            <div class="alert alert-danger">
                Error al obtener tipo de cambio. Se está usando el valor por defecto.
            </div>
        {% endif %}
    </div>
</div>

<script>
// JavaScript para actualizar tipo de cambio vía AJAX
document.getElementById('actualizar-tipo-cambio').addEventListener('click', function() {
    fetch('/ventas/tipo-cambio/api/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Tipo de cambio actual: ${data.tipo_cambio}`);
                location.reload(); // Recargar para mostrar nuevo valor
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            alert('Error de conexión');
        });
});
</script>
"""