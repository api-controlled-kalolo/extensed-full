from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from ventas.forms import CotizacionForm, DetallesCotizacionesInLineFormSet
from django.template import Template, Context
from django.template.loader import render_to_string
from services.gotenberg_engine import html_to_pdf_bytes_gotenberg 
from datetime import datetime
from ventas.models import Contacto, Cliente, Cotizacion, Detalles_Cotizacion
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def generar_cotizacion(request):
  if request.method == 'GET':
    return render(request, 'cotizaciones/crear_cotizacion.html', {
      'form': CotizacionForm(),
      'detalles_formset': DetallesCotizacionesInLineFormSet()
    })
  else:
    try:
      form = CotizacionForm(request.POST)
      detalles = DetallesCotizacionesInLineFormSet(request.POST)
      if form.is_valid():
        new_cotizacion = form.save(commit=False)
        new_cotizacion.save()
        
        detalles = DetallesCotizacionesInLineFormSet(request.POST, instance=new_cotizacion)
        
        if detalles.is_valid():
          detalles.save()
          
          # Usar las propiedades calculadas del modelo en lugar de cálculo manual
          
          plantilla_html = r"""
          <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cotización {{ numero_cotizacion }}</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.4;
                    color: #2c3e50;
                    background-color: #ffffff;
                    font-size: 11px;
                }
                
                .container {
                    max-width: 210mm;
                    margin: 0 auto;
                    padding: 8mm 15mm 10mm 15mm;
                    background: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 15px;
                    border-bottom: 3px solid #34495e;
                }
                
                .logo-section {
                    flex: 1;
                }
                
                .logo {
                    height: 120px;
                    max-width: 300px;
                    object-fit: contain;
                }
                
                .company-info {
                    flex: 1;
                    text-align: right;
                    font-size: 11px;
                    color: #2c3e50;
                    line-height: 1.4;
                }
                
                .company-info strong {
                    font-size: 12px;
                    color: #34495e;
                }
                
                .quote-title {
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 12px 25px;
                    margin: 15px 0;
                    text-align: center;
                    font-size: 17px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                
                .client-info {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                
                .info-card {
                    flex: 1;
                    background: #fafbfc;
                    padding: 16px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .info-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #3498db, #2980b9);
                    border-radius: 10px 10px 0 0;
                }
                
                .info-card h3 {
                    color: #2c3e50;
                    font-size: 13px;
                    margin-bottom: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    border-bottom: 2px solid #bdc3c7;
                    padding-bottom: 6px;
                }
                
                .info-card .info-row {
                    display: flex;
                    margin: 6px 0;
                    align-items: center;
                }
                
                .info-card .label {
                    font-weight: 600;
                    color: #34495e;
                    min-width: 90px;
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }
                
                .info-card .value {
                    color: #2c3e50;
                    font-weight: 500;
                    font-size: 11px;
                    flex: 1;
                }
                
                .details-section {
                    margin: 18px 0;
                }
                
                .details-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                }
                
                .details-table th {
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    font-weight: 700;
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    border-right: 1px solid rgba(255,255,255,0.1);
                }
                
                .details-table th:last-child {
                    border-right: none;
                }
                
                .details-table td {
                    padding: 10px 8px;
                    text-align: center;
                    border-bottom: 1px solid #ecf0f1;
                    font-size: 10px;
                    vertical-align: middle;
                }
                
                .details-table tbody tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                
                .details-table tbody tr:hover {
                    background-color: #e8f4f8;
                }
                
                .description-cell {
                    text-align: left !important;
                    max-width: 160px;
                    word-wrap: break-word;
                    line-height: 1.4;
                    color: #2c3e50;
                    padding-left: 15px !important;
                }
                
                .price-cell {
                    font-weight: 700;
                    color: #34495e;
                    font-size: 11px;
                }
                
                /* MODIFICACIÓN 1: Total general optimizado */
                .subtotal-row {
                    background: #f8f9fa !important;
                    color: #495057 !important;
                    font-weight: 600 !important;
                }
                
                .igv-row {
                    background: #e9ecef !important;
                    color: #495057 !important;
                    font-weight: 600 !important;
                }
                
                .total-row {
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%) !important;
                    color: white !important;
                    font-weight: 700 !important;
                }
                
                .subtotal-row td, .igv-row td, .total-row td {
                    border-bottom: none !important;
                    padding: 12px 8px !important;
                    font-size: 11px !important;
                    font-weight: 700 !important;
                    text-align: center !important;
                }
                
                .total-label-cell {
                    text-align: center !important;
                    letter-spacing: 0.8px !important;
                    text-transform: uppercase !important;
                    font-size: 11px !important;
                }
                
                .total-amount-cell {
                    font-size: 12px !important;
                    font-weight: 800 !important;
                    letter-spacing: 0.5px !important;
                    text-align: center !important;
                }
                
                /* MODIFICACIÓN 2: Nueva estructura de layout */
                .bottom-section {
                    margin-top: 20px;
                }
                
                .main-content-section {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 15px;
                    align-items: stretch;
                    flex-wrap: nowrap;
                }
                
                .scope-section {
                    /* Fija columna izquierda al 66% */
                    flex: 0 0 66%;
                    max-width: 66%;
                    background: #fafbfc;
                    padding: 18px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .scope-section::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #34495e, #2c3e50);
                    border-radius: 8px 8px 0 0;
                }
                
                .scope-section h3 {
                    color: #2c3e50;
                    font-size: 13px;
                    margin-bottom: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    border-bottom: 2px solid #bdc3c7;
                    padding-bottom: 6px;
                }
                
                .scope-content {
                    font-size: 10px;
                    line-height: 1.4;
                    color: #34495e;
                    text-align: justify;
                }
                
                .right-info-section {
                    /* Fija columna derecha al 34% */
                    flex: 0 0 34%;
                    max-width: 34%;
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }
                
                .bank-info-card {
                    background: #fafbfc;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .bank-info-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #95a5a6, #7f8c8d);
                    border-radius: 8px 8px 0 0;
                }
                
                .bank-info-card h4 {
                    color: #2c3e50;
                    font-size: 11px;
                    margin-bottom: 10px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.6px;
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 5px;
                }
                
                .bank-info-card p {
                    font-size: 10px;
                    line-height: 1.4;
                    color: #34495e;
                    margin: 4px 0;
                }
                
                .bank-account {
                    font-weight: 700;
                    color: #2c3e50;
                    font-size: 10px;
                }
                
                .terms-card {
                    background: #fafbfc;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .terms-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #95a5a6, #7f8c8d);
                    border-radius: 8px 8px 0 0;
                }
                
                .terms-content {
                    margin-bottom: 15px;
                }
                
                .terms-content:last-child {
                    margin-bottom: 0;
                }
                
                .terms-label {
                    color: #2c3e50;
                    font-size: 10px;
                    margin-bottom: 5px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .terms-value {
                    font-size: 12px;
                    font-weight: 700;
                    color: #2c3e50;
                    text-align: center;
                    padding: 6px;
                    background: #ecf0f1;
                    border-radius: 5px;
                }
                
                .exchange-note {
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #e1e8ed;
                    font-size: 9px;
                    color: #34495e;
                    margin: 12px 0;
                    text-align: center;
                    font-style: italic;
                }
                
                .certification {
                    text-align: center;
                    margin-top: 15px;
                    padding-top: 15px;
                    border-top: 2px solid #ecf0f1;
                }
                
                .cert-logo {
                    height: 100px;
                    margin-bottom: 8px;
                    opacity: 0.9;
                }
                
                .cert-text {
                    font-size: 10px;
                    color: #7f8c8d;
                    font-style: italic;
                    font-weight: 500;
                }
                
                @media print {
                    .container {
                        box-shadow: none;
                        padding: 8mm 10mm;
                    }
                    
                    body {
                        font-size: 9px;
                    }
                    
                    .details-table th,
                    .details-table td {
                        padding: 6px 4px;
                        font-size: 8px;
                    }
                    
                    .quote-title {
                        font-size: 15px;
                        padding: 10px 20px;
                        margin: 10px 0;
                    }
                    
                    .total-row td {
                        font-size: 9px !important;
                        padding: 10px 4px !important;
                    }
                    
                    .total-amount-cell {
                        font-size: 10px !important;
                    }
                    
                    /* Mantener dos columnas también en impresión */
                    .main-content-section {
                        display: flex;
                        flex-direction: row;
                        gap: 16px;
                        flex-wrap: nowrap;
                        align-items: stretch;
                    }
                    .scope-section { flex: 0 0 66%; max-width: 66%; }
                    .right-info-section { flex: 0 0 34%; max-width: 34%; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="logo-section">
                        <img src="https://i.ibb.co/wFRJS8cw/textoanhe-removebg-preview.png" alt="Logo Empresa" class="logo">
                    </div>
                <div class="company-info">
                    <strong>{{ cotizacion.razon_social }}</strong><br>
                    RUC: {{ cotizacion.ruc }}<br>
                    {{ cotizacion.direccion }}<br>
                    Cel: {{ cotizacion.celular }}<br>
                    {{ user.email }}
                </div>
                </div>
                
                <!-- Título de Cotización -->
                <div class="quote-title">
                    COTIZACIÓN {{ cotizacion.numero_cotizacion }}
                </div>
                
                <!-- Información del Cliente -->
                <div class="client-info">
                    <div class="info-card">
                        <h3>Información del Cliente</h3>
                        <div class="info-row">
                            <span class="label">RUC:</span>
                            <span class="value">{% if cotizacion.cliente %}{{ cotizacion.cliente.ruc }}{% else %}{{ cotizacion.ruc }}{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Empresa:</span>
                            <span class="value">{% if cotizacion.cliente %}{{ cotizacion.cliente.razon_social }}{% else %}{{ cotizacion.razon_social }}{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Fecha:</span>
                            <span class="value">{{ cotizacion.fecha_creacion|date:"d/m/Y" }}</span>
                        </div>
                    </div>
                    <div class="info-card">
                        <h3>Información de Contacto</h3>
                        <div class="info-row">
                            <span class="label">Contacto:</span>
                            <span class="value">{% if cotizacion.contacto %}{{ cotizacion.contacto.nombres }} {{ cotizacion.contacto.apellidos }}{% else %}--{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Correo:</span>
                            <span class="value">{% if cotizacion.contacto %}{{ cotizacion.contacto.correo }}{% else %}--{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Celular:</span>
                            <span class="value">{% if cotizacion.contacto %}{{ cotizacion.contacto.Celular }}{% else %}--{% endif %}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Tabla de Detalles -->
                <div class="details-section">
                    <table class="details-table">
                        <thead>
                            <tr>
                                <th style="width: 8%;">ITEM</th>
                                <th style="width: 50%;">DESCRIPCIÓN</th>
                                <th style="width: 12%;">UNIDAD</th>
                                <th style="width: 10%;">CANT.</th>
                                <th style="width: 12%;">P. UNIT.</th>
                                <th style="width: 12%;">SUBTOTAL</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for detalle in detalles %}
                            <tr>
                                <td>{{ forloop.counter }}</td>
                                <td class="description-cell">{{ detalle.descripcion }}</td>
                                <td>{{ detalle.unidad }}</td>
                                <td>{{ detalle.cantidad }}</td>
                                <td class="price-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ detalle.precio_unitario|floatformat:2 }}
                                </td>
                                <td class="price-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ detalle.precio_total|floatformat:2 }}
                                </td>
                            </tr>
                            {% endfor %}
                            <!-- Filas de totales mejoradas -->
                            <tr class="subtotal-row">
                                <td colspan="5" class="total-label-cell">SUBTOTAL</td>
                                <td class="total-amount-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ subtotal|floatformat:2 }}
                                </td>
                            </tr>
                            {% if cotizacion.incluye_igv %}
                            <tr class="igv-row">
                                <td colspan="5" class="total-label-cell">IGV (18%)</td>
                                <td class="total-amount-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ igv_monto|floatformat:2 }}
                                </td>
                            </tr>
                            {% endif %}
                            <tr class="total-row">
                                <td colspan="5" class="total-label-cell">TOTAL GENERAL</td>
                                <td class="total-amount-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ total_con_igv|floatformat:2 }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- MODIFICACIÓN 2: Nueva estructura de contenido -->
                <div class="bottom-section">
                    <div class="main-content-section">
                        <!-- Sección de Alcance (Izquierda) -->
                        <div class="scope-section">
                            <h3>Alcance de la Oferta</h3>
                            <div class="scope-content">
                                {{ cotizacion.alcance_total_oferta|linebreaks }}
                            </div>
                        </div>
                        
                        <!-- Información Lateral (Derecha) -->
                        <div class="right-info-section">
                            <!-- Cuentas Bancarias -->
                            <div class="bank-info-card">
                                <h4>Cuentas Bancarias</h4>
                                <p><span class="bank-account">INTERBANK SOLES</span></p>
                                <p>200-3003321671003-200-003003321671-31</p>
                                <p><span class="bank-account">INTERBANK DÓLARES</span></p>
                                <p>200-3007198016003-200-003007198016-30</p>
                                <p><span class="bank-account">DETRACCIÓN</span></p>
                                <p>00-059-144693</p>
                            </div>
                            
                            <!-- Términos -->
                            <div class="terms-card">
                                <div class="terms-content">
                                    <div class="terms-label">Validez de la Oferta</div>
                                    <div class="terms-value">{{ cotizacion.validez_oferta|default:"30 días" }}</div>
                                </div>
                                <div class="terms-content">
                                    <div class="terms-label">Forma de Pago</div>
                                    <div class="terms-value">{{ cotizacion.forma_pago|default:"AL CONTADO" }}</div>
                                </div>
                                <div class="terms-content">
                                    <div class="terms-label">Moneda</div>
                                    <div class="terms-value">{{ cotizacion.moneda|default:"Soles" }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Nota de Tipo de Cambio -->
                <div class="exchange-note">
                    {% if cotizacion.moneda == 'Dolares' %}
                        Para la conversión a soles, se empleará el tipo de cambio de S/ {{ tipo_cambio_efectivo|floatformat:3 }} (BCR + margen) vigente en la fecha de la cotización.
                    {% else %}
                        Precios expresados en {{ cotizacion.moneda|default:"Soles" }}.
                        {% if cotizacion.moneda == 'Soles' and tipo_cambio_efectivo %}
                            Tipo de cambio referencial USD: S/ {{ tipo_cambio_efectivo|floatformat:3 }}
                        {% endif %}
                    {% endif %}
                </div>
                
                <!-- Certificación -->
                <div class="certification">
                    <img src="https://www.cns.com.pe/wp-content/uploads/2021/12/HODELPE-1-HOMOLOGADO-POR-HODELPE-1-e1640187408664-300x295.jpg" alt="Certificación" class="cert-logo">
                    <div class="cert-text">Empresa certificada y homologada</div>
                </div>
            </div>
        </body>
        </html>
          """
          
          html_rendered = Template(plantilla_html).render(Context({
            'cotizacion': new_cotizacion,
            'detalles': new_cotizacion.detalles.all(),
            'subtotal': new_cotizacion.subtotal,
            'igv_monto': new_cotizacion.igv_monto,
            'total_con_igv': new_cotizacion.total_con_igv,
            'total_soles': new_cotizacion.total_soles,
            'total_dolares': new_cotizacion.total_dolares,
            'tipo_cambio_efectivo': new_cotizacion.tipo_cambio_efectivo,
            'user': request.user
          }))
          
          # Convertir a PDF
          pdf_bytes = html_to_pdf_bytes_gotenberg(html_rendered)
          if not pdf_bytes:
            return render(request, 'cotizaciones/crear_cotizacion.html', {
              'form': CotizacionForm(),
              'error': 'No se pudo generar el PDF, revisar el serivicio del PDF'
            })
          
          # DESCARGA AUTOMÁTICA (sin previsualización)
          response = HttpResponse(pdf_bytes,content_type='application/pdf')
          response['Content-Disposition'] = f'attachment; filename="cot00{new_cotizacion.pk}{datetime.now().year}.pdf"'
          
          print("PDF generado con éxito")
          
          return response
        else:
          # Errores en el formset (tabla equipos)
          campos_con_error = []
          for f in detalles:
            for c in f.errors.keys():
              campos_con_error.append(c)
              mensaje_error = "Hay errores en la tabla de detalles: " + ", ".join(set(campos_con_error)) if campos_con_error else "Hay errores en la tabla de detalles."
              return render(request, 'cotizaciones/crear_cotizacion.html', {
                'form': form,                 # mantenemos datos del aingresados
                'detalles': detalles,
                'error': mensaje_error,
              })
          
      # Error en la Validación de Datos 
      else:
        campos_con_error = [form.fields[c].label or c for c in form.errors.keys()]
        mensaje_error = "Hay un error en los campos siguientes: "+", ".join(campos_con_error)
        return render('cotizaciones/crear_cotizacion.html', {
          'form': form,
          'detalles': detalles,
          'error': mensaje_error,
        })
          
    except ValueError as e:
      return render(request, 'cotizaciones/crear_cotizacion.html', {
        'form': form,
        'detalles': detalles,
        'error': f"Hay un error de conexion en el sistema {str(e)}",
      })

@login_required 
def menu_cotizaciones(request):
  return render(request, 'cotizaciones/opcciones_cotizaciones.html')


@login_required
def contactos_por_cliente_api(request, cliente_id: int):
    """Devuelve contactos del cliente dado en formato JSON.

    Response:
    { "results": [ {"id": int, "label": "Nombre Apellido - Cargo"}, ... ] }
    """
    if request.method != 'GET':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    qs = Contacto.objects.filter(cliente_principal_id=cliente_id).order_by('nombres', 'apellidos')
    results = [{
            "id": c.id,
            "label": f"{c.nombres} {c.apellidos} - {c.cargo}".strip()
        } for c in qs]
    return JsonResponse({"results": results})


@login_required
def obtener_datos_cliente_api(request, cliente_id: int):
    """
    Devuelve los datos del cliente (RUC, Razón Social, Dirección)
    
    Response:
    { "ruc": "...", "razon_social": "...", "direccion": "..." }
    """
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        return JsonResponse({
            "ruc": cliente.ruc,
            "razon_social": cliente.razon_social,
            "direccion": cliente.direccion
        })
    except Cliente.DoesNotExist:
        return JsonResponse({"error": "Cliente no encontrado"}, status=404)


@login_required
def obtener_datos_contacto_api(request, contacto_id: int):
    """
    Devuelve los datos del contacto (Correo, Celular)
    
    Response:
    { "correo": "...", "celular": "..." }
    """
    try:
        contacto = Contacto.objects.get(id=contacto_id)
        return JsonResponse({
            "correo": contacto.correo,
            "celular": contacto.Celular
        })
    except Contacto.DoesNotExist:
        return JsonResponse({"error": "Contacto no encontrado"}, status=404)

@login_required
def cotizaciones_list(request):
    """
    Listado de cotizaciones con búsqueda, filtros por cliente y rango de fechas,
    ordenamiento por columnas y paginación.
    """
    # Base Query con relaciones optimizadas
    qs = Cotizacion.objects.select_related(
        'cliente__proyecto_principal', 
        'contacto'
    ).prefetch_related('detalles')

    # --- Filtros ---
    q = (request.GET.get('q') or '').strip()
    cliente_id = (request.GET.get('cliente') or '').strip()
    desde = (request.GET.get('desde') or '').strip()
    hasta = (request.GET.get('hasta') or '').strip()
    estado = (request.GET.get('estado') or '').strip()

    if q:
        qs = qs.filter(
            Q(numero_cotizacion__icontains=q) |
            Q(nombre_cotizacion__icontains=q) |
            Q(cliente__ruc__icontains=q) |
            Q(cliente__razon_social__icontains=q) |
            Q(correo__icontains=q) |
            Q(celular__icontains=q) |
            Q(direccion__icontains=q)
        )

    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    if desde:
        qs = qs.filter(fecha_creacion__gte=desde)
    if hasta:
        qs = qs.filter(fecha_creacion__lte=hasta)
        
    if estado:
        qs = qs.filter(estado_coti=estado)

    # --- Ordenamiento (whitelist) ---
    order = (request.GET.get('order') or '-fecha_creacion').strip()
    allowed = {
        'fecha_creacion': 'fecha_creacion',
        '-fecha_creacion': '-fecha_creacion',
        'numero_cotizacion': 'numero_cotizacion',
        '-numero_cotizacion': '-numero_cotizacion',
        'nombre_cotizacion': 'nombre_cotizacion',
        '-nombre_cotizacion': '-nombre_cotizacion',
        'cliente': 'cliente__razon_social',
        '-cliente': '-cliente__razon_social',
        'estado_coti': 'estado_coti',
        '-estado_coti': '-estado_coti',
        'fecha_actualizacion_estado': 'fecha_actualizacion_estado',
        '-fecha_actualizacion_estado': '-fecha_actualizacion_estado',
    }
    qs = qs.order_by(allowed.get(order, '-fecha_creacion'))

    # --- Paginación ---
    paginator = Paginator(qs, 15)  # 15 por página para mejor visualización
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    # Utilidad para conservar querystring sin un parámetro
    def query_without(param):
        params = request.GET.dict()
        params.pop(param, None)
        from urllib.parse import urlencode
        return urlencode(params)

    # Para el filtro de clientes
    try:
        clientes = Cliente.objects.select_related('proyecto_principal').order_by('razon_social')
    except Exception:
        clientes = []

    # Estados disponibles para el filtro
    estados_choices = [
        ('', 'Todos los estados'),
        ('En Negociación', 'En Negociación'),
        ('Ganado', 'Ganado'),
        ('Perdida', 'Perdida'),
    ]

    ctx = {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'q': q,
        'cliente_id': cliente_id,
        'desde': desde,
        'hasta': hasta,
        'estado': estado,
        'order': order,
        'clientes': clientes,
        'estados_choices': estados_choices,
        'query_without_page': query_without('page'),
        'query_without_order': query_without('order'),
    }
    return render(request, 'cotizaciones/cotizaciones_list.html', ctx)


@login_required
@require_http_methods(["POST"])
def cambiar_estado_cotizacion(request, pk):
    """
    Vista AJAX para cambiar el estado de una cotización.
    """
    try:
        cotizacion = get_object_or_404(Cotizacion, pk=pk)
        nuevo_estado = request.POST.get('estado')
        
        # Validar estado
        estados_validos = ['En Negociación', 'Ganado', 'Perdida']
        if nuevo_estado not in estados_validos:
            return JsonResponse({
                'success': False, 
                'error': 'Estado no válido'
            }, status=400)
        
        # Actualizar estado
        cotizacion.estado_coti = nuevo_estado
        cotizacion.fecha_actualizacion_estado = timezone.now()
        cotizacion.save(update_fields=['estado_coti', 'fecha_actualizacion_estado'])
        
        return JsonResponse({
            'success': True,
            'nuevo_estado': nuevo_estado,
            'fecha_actualizacion': cotizacion.fecha_actualizacion_estado.strftime('%d/%m/%Y %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import (
    Sum, Count, F, Value, Q
)
from django.db.models.functions import Coalesce, TruncMonth, TruncDate
from django.shortcuts import render
from django.utils.timezone import make_naive
from django.contrib import messages
from django.urls import reverse

IGV_RATE = Decimal("0.18")

def cotizaciones_dashboard(request):
    """
    Dashboard con KPIs y gráficos:
    - KPIs: #cotizaciones, #ítems, Subtotal, IGV, Total, Ticket promedio, % crecimiento vs. periodo anterior
    - Series: Cotizaciones por día (últimos 30d), Monto por mes (últimos 12 meses)
    - Top: Top clientes por monto
    - Mix: Unidades (UNIDAD/DECENA)
    Filtros: rango de fechas (desde, hasta) y cliente
    """
    # ------- Filtros -------
    hoy = date.today()
    default_desde = hoy - timedelta(days=90)  # últimos 90 días por defecto
    desde_str = (request.GET.get('desde') or "").strip()
    hasta_str = (request.GET.get('hasta') or "").strip()
    cliente_id = (request.GET.get('cliente') or "").strip()

    try:
        desde = date.fromisoformat(desde_str) if desde_str else default_desde
    except Exception:
        desde = default_desde
    try:
        hasta = date.fromisoformat(hasta_str) if hasta_str else hoy
    except Exception:
        hasta = hoy

    base_q = Q(fecha_creacion__gte=desde) & Q(fecha_creacion__lte=hasta)
    if cliente_id:
        base_q &= Q(cliente_id=cliente_id)

    # ------- QuerySets filtrados -------
    qs_cot = Cotizacion.objects.filter(base_q).select_related('cliente')
    qs_det = Detalles_Cotizacion.objects.filter(
        cotizacion_principal__in=qs_cot
    )

    # ------- KPIs principales -------
    # Subtotal = sum(cantidad * precio_unitario) en detalles
    from django.db.models import DecimalField
    agg_sub = qs_det.aggregate(
        subtotal=Coalesce(Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField()), Value(0, output_field=DecimalField()))
    )
    subtotal = Decimal(agg_sub['subtotal'] or 0)
    igv = (subtotal * IGV_RATE).quantize(Decimal("0.01"))
    total = (subtotal + igv).quantize(Decimal("0.01"))

    total_cotizaciones = qs_cot.count()
    total_items = qs_det.aggregate(cnt=Coalesce(Count('id'), Value(0)))['cnt'] or 0
    ticket_prom = (total / total_cotizaciones).quantize(Decimal("0.01")) if total_cotizaciones else Decimal("0.00")

    # Crecimiento vs. periodo anterior (mide cotizaciones)
    periodo_dias = max((hasta - desde).days, 1)
    prev_desde = desde - timedelta(days=periodo_dias)
    prev_hasta = desde - timedelta(days=1)
    qs_prev_cot = Cotizacion.objects.filter(
        fecha_creacion__gte=prev_desde,
        fecha_creacion__lte=prev_hasta
    )
    if cliente_id:
        qs_prev_cot = qs_prev_cot.filter(cliente_id=cliente_id)
    prev_count = qs_prev_cot.count()
    growth_pct = 0.0
    if prev_count and total_cotizaciones is not None:
        growth_pct = round(((total_cotizaciones - prev_count) / prev_count) * 100.0, 2)
    elif total_cotizaciones and not prev_count:
        growth_pct = 100.0

    # ------- Series: Cotizaciones por día (últimos 30 días) -------
    last_30_from = hoy - timedelta(days=29)
    qs_30 = Cotizacion.objects.filter(
        fecha_creacion__gte=last_30_from,
        fecha_creacion__lte=hoy
    )
    if cliente_id:
        qs_30 = qs_30.filter(cliente_id=cliente_id)

    by_day = (
        qs_30
        .annotate(d=TruncDate('fecha_creacion'))
        .values('d')
        .annotate(cnt=Count('id'))
        .order_by('d')
    )
    series_days = []
    series_counts = []
    # normalizamos para que estén los 30 días completos
    for i in range(30):
        d = last_30_from + timedelta(days=i)
        series_days.append(d.isoformat())
        match = next((x for x in by_day if x['d'] == d), None)
        series_counts.append(int(match['cnt']) if match else 0)

    # ------- Series: Monto por mes (últimos 12 meses) -------
    last_12_from = (hoy.replace(day=1) - timedelta(days=365))  # aprox 12 meses
    qs_cot_12 = Cotizacion.objects.filter(fecha_creacion__gte=last_12_from, fecha_creacion__lte=hoy)
    if cliente_id:
        qs_cot_12 = qs_cot_12.filter(cliente_id=cliente_id)
    qs_det_12 = Detalles_Cotizacion.objects.filter(cotizacion_principal__in=qs_cot_12)

    by_month_amount = (
        qs_det_12
        .annotate(m=TruncMonth('cotizacion_principal__fecha_creacion'))
        .values('m')
        .annotate(monto=Coalesce(Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField()), Value(0, output_field=DecimalField())))
        .order_by('m')
    )
    months_labels = []
    months_amounts = []
    # generamos meses desde last_12_from -> hoy (inclusive)
    cur = last_12_from.replace(day=1)
    end = hoy.replace(day=1)
    while cur <= end:
        months_labels.append(cur.strftime("%Y-%m"))
        match = next((x for x in by_month_amount if x['m'] and x['m'].strftime("%Y-%m") == cur.strftime("%Y-%m")), None)
        monto = Decimal(match['monto']) if match else Decimal("0")
        months_amounts.append(float(monto))
        # avanzar 1 mes
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)

    # ------- Top clientes por monto -------
    top_raw = (
        qs_det
        .values('cotizacion_principal__cliente_id')
        .annotate(monto=Coalesce(Sum(F('cantidad') * F('precio_unitario'), output_field=DecimalField()), Value(0, output_field=DecimalField())))
        .order_by('-monto')[:7]
    )
    # Obtener nombres de clientes
    client_ids = [r['cotizacion_principal__cliente_id'] for r in top_raw if r['cotizacion_principal__cliente_id']]
    clientes_map = {c.id: str(c) for c in Cliente.objects.filter(id__in=client_ids)} if client_ids else {}
    top_clients_labels = [clientes_map.get(r['cotizacion_principal__cliente_id'], f"ID {r['cotizacion_principal__cliente_id']}") for r in top_raw]
    top_clients_values = [float(r['monto']) for r in top_raw]

    # ------- Mix de unidades -------
    unidades_raw = (
        qs_det
        .values('unidad')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')
    )
    # Creamos las listas para el gráfico de unidades
    unidades_labels = [r['unidad'] or '—' for r in unidades_raw]  # por si hay vacío
    unidades_counts = [int(r['cnt']) for r in unidades_raw]

    # ------- Contexto -------
    try:
        clientes = Cliente.objects.all().order_by('id')
    except Exception:
        clientes = []

    ctx = {
        # filtros
        'desde': desde.isoformat(),
        'hasta': hasta.isoformat(),
        'cliente_id': cliente_id,
        'clientes': clientes,

        # KPIs
        'total_cotizaciones': total_cotizaciones,
        'total_items': total_items,
        'subtotal': f"{subtotal:.2f}",
        'igv': f"{igv:.2f}",
        'total': f"{total:.2f}",
        'ticket_prom': f"{ticket_prom:.2f}",
        'growth_pct': growth_pct,

        # series (se inyectan como JSON)
        'series_days': series_days,
        'series_counts': series_counts,
        'months_labels': months_labels,
        'months_amounts': months_amounts,
        'top_clients_labels': top_clients_labels,
        'top_clients_values': top_clients_values,
        'unidades_labels': unidades_labels,
        'unidades_counts': unidades_counts,
    }
    # El template está en ventas/templates/cotizaciones/cotizaciones_dashboard.html
    return render(request, 'cotizaciones/cotizaciones_dashboard.html', ctx)


@login_required
def visualizar_pdf_cotizacion(request, pk):
    """
    Vista para visualizar el PDF de una cotización existente en el navegador
    Reutiliza el mismo template HTML completo de generar_cotizacion
    """
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    
    try:
        # Usar el mismo template HTML completo que generar_cotizacion
        plantilla_html = r"""
          <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cotización {{ numero_cotizacion }}</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.4;
                    color: #2c3e50;
                    background-color: #ffffff;
                    font-size: 11px;
                }
                
                .container {
                    max-width: 210mm;
                    margin: 0 auto;
                    padding: 8mm 15mm 10mm 15mm;
                    background: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 15px;
                    border-bottom: 3px solid #34495e;
                }
                
                .logo-section {
                    flex: 1;
                }
                
                .logo {
                    height: 120px;
                    max-width: 300px;
                    object-fit: contain;
                }
                
                .company-info {
                    flex: 1;
                    text-align: right;
                    font-size: 11px;
                    color: #2c3e50;
                    line-height: 1.4;
                }
                
                .company-info strong {
                    font-size: 12px;
                    color: #34495e;
                }
                
                .quote-title {
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 12px 25px;
                    margin: 15px 0;
                    text-align: center;
                    font-size: 17px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                
                .client-info {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                
                .info-card {
                    flex: 1;
                    background: #fafbfc;
                    padding: 16px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .info-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #3498db, #2980b9);
                    border-radius: 10px 10px 0 0;
                }
                
                .info-card h3 {
                    color: #2c3e50;
                    font-size: 13px;
                    margin-bottom: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    border-bottom: 2px solid #bdc3c7;
                    padding-bottom: 6px;
                }
                
                .info-card .info-row {
                    display: flex;
                    margin: 6px 0;
                    align-items: center;
                }
                
                .info-card .label {
                    font-weight: 600;
                    color: #34495e;
                    min-width: 90px;
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }
                
                .info-card .value {
                    color: #2c3e50;
                    font-weight: 500;
                    font-size: 11px;
                    flex: 1;
                }
                
                .details-section {
                    margin: 18px 0;
                }
                
                .details-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                }
                
                .details-table th {
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    font-weight: 700;
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    border-right: 1px solid rgba(255,255,255,0.1);
                }
                
                .details-table th:last-child {
                    border-right: none;
                }
                
                .details-table td {
                    padding: 10px 8px;
                    text-align: center;
                    border-bottom: 1px solid #ecf0f1;
                    font-size: 10px;
                    vertical-align: middle;
                }
                
                .details-table tbody tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
                
                .details-table tbody tr:hover {
                    background-color: #e8f4f8;
                }
                
                .description-cell {
                    text-align: left !important;
                    max-width: 160px;
                    word-wrap: break-word;
                    line-height: 1.4;
                    color: #2c3e50;
                    padding-left: 15px !important;
                }
                
                .price-cell {
                    font-weight: 700;
                    color: #34495e;
                    font-size: 11px;
                }
                
                /* MODIFICACIÓN 1: Total general optimizado */
                .subtotal-row {
                    background: #f8f9fa !important;
                    color: #495057 !important;
                    font-weight: 600 !important;
                }
                
                .igv-row {
                    background: #e9ecef !important;
                    color: #495057 !important;
                    font-weight: 600 !important;
                }
                
                .total-row {
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%) !important;
                    color: white !important;
                    font-weight: 700 !important;
                }
                
                .subtotal-row td, .igv-row td, .total-row td {
                    border-bottom: none !important;
                    padding: 12px 8px !important;
                    font-size: 11px !important;
                    font-weight: 700 !important;
                    text-align: center !important;
                }
                
                .total-label-cell {
                    text-align: center !important;
                    letter-spacing: 0.8px !important;
                    text-transform: uppercase !important;
                    font-size: 11px !important;
                }
                
                .total-amount-cell {
                    font-size: 12px !important;
                    font-weight: 800 !important;
                    letter-spacing: 0.5px !important;
                    text-align: center !important;
                }
                
                /* MODIFICACIÓN 2: Nueva estructura de layout */
                .bottom-section {
                    margin-top: 20px;
                }
                
                .main-content-section {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 15px;
                    align-items: stretch;
                    flex-wrap: nowrap;
                }
                
                .scope-section {
                    /* Fija columna izquierda al 66% */
                    flex: 0 0 66%;
                    max-width: 66%;
                    background: #fafbfc;
                    padding: 18px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .scope-section::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #34495e, #2c3e50);
                    border-radius: 8px 8px 0 0;
                }
                
                .scope-section h3 {
                    color: #2c3e50;
                    font-size: 13px;
                    margin-bottom: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    border-bottom: 2px solid #bdc3c7;
                    padding-bottom: 6px;
                }
                
                .scope-content {
                    font-size: 10px;
                    line-height: 1.4;
                    color: #34495e;
                    text-align: justify;
                }
                
                .right-info-section {
                    /* Fija columna derecha al 34% */
                    flex: 0 0 34%;
                    max-width: 34%;
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }
                
                .bank-info-card {
                    background: #fafbfc;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .bank-info-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #95a5a6, #7f8c8d);
                    border-radius: 8px 8px 0 0;
                }
                
                .bank-info-card h4 {
                    color: #2c3e50;
                    font-size: 11px;
                    margin-bottom: 10px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.6px;
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 5px;
                }
                
                .bank-info-card p {
                    font-size: 10px;
                    line-height: 1.4;
                    color: #34495e;
                    margin: 4px 0;
                }
                
                .bank-account {
                    font-weight: 700;
                    color: #2c3e50;
                    font-size: 10px;
                }
                
                .terms-card {
                    background: #fafbfc;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e1e8ed;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
                    position: relative;
                }
                
                .terms-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #95a5a6, #7f8c8d);
                    border-radius: 8px 8px 0 0;
                }
                
                .terms-content {
                    margin-bottom: 15px;
                }
                
                .terms-content:last-child {
                    margin-bottom: 0;
                }
                
                .terms-label {
                    color: #2c3e50;
                    font-size: 10px;
                    margin-bottom: 5px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .terms-value {
                    font-size: 12px;
                    font-weight: 700;
                    color: #2c3e50;
                    text-align: center;
                    padding: 6px;
                    background: #ecf0f1;
                    border-radius: 5px;
                }
                
                .exchange-note {
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #e1e8ed;
                    font-size: 9px;
                    color: #34495e;
                    margin: 12px 0;
                    text-align: center;
                    font-style: italic;
                }
                
                .certification {
                    text-align: center;
                    margin-top: 15px;
                    padding-top: 15px;
                    border-top: 2px solid #ecf0f1;
                }
                
                .cert-logo {
                    height: 100px;
                    margin-bottom: 8px;
                    opacity: 0.9;
                }
                
                .cert-text {
                    font-size: 10px;
                    color: #7f8c8d;
                    font-style: italic;
                    font-weight: 500;
                }
                
                @media print {
                    .container {
                        box-shadow: none;
                        padding: 8mm 10mm;
                    }
                    
                    body {
                        font-size: 9px;
                    }
                    
                    .details-table th,
                    .details-table td {
                        padding: 6px 4px;
                        font-size: 8px;
                    }
                    
                    .quote-title {
                        font-size: 15px;
                        padding: 10px 20px;
                        margin: 10px 0;
                    }
                    
                    .total-row td {
                        font-size: 9px !important;
                        padding: 10px 4px !important;
                    }
                    
                    .total-amount-cell {
                        font-size: 10px !important;
                    }
                    
                    /* Mantener dos columnas también en impresión */
                    .main-content-section {
                        display: flex;
                        flex-direction: row;
                        gap: 16px;
                        flex-wrap: nowrap;
                        align-items: stretch;
                    }
                    .scope-section { flex: 0 0 66%; max-width: 66%; }
                    .right-info-section { flex: 0 0 34%; max-width: 34%; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="logo-section">
                        <img src="https://i.ibb.co/wFRJS8cw/textoanhe-removebg-preview.png" alt="Logo Empresa" class="logo">
                    </div>
                <div class="company-info">
                    <strong>{{ cotizacion.razon_social }}</strong><br>
                    RUC: {{ cotizacion.ruc }}<br>
                    {{ cotizacion.direccion }}<br>
                    Cel: {{ cotizacion.celular }}<br>
                    {{ user.email }}
                </div>
                </div>
                
                <!-- Título de Cotización -->
                <div class="quote-title">
                    COTIZACIÓN {{ cotizacion.numero_cotizacion }}
                </div>
                
                <!-- Información del Cliente -->
                <div class="client-info">
                    <div class="info-card">
                        <h3>Información del Cliente</h3>
                        <div class="info-row">
                            <span class="label">RUC:</span>
                            <span class="value">{% if cotizacion.cliente %}{{ cotizacion.cliente.ruc }}{% else %}{{ cotizacion.ruc }}{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Empresa:</span>
                            <span class="value">{% if cotizacion.cliente %}{{ cotizacion.cliente.razon_social }}{% else %}{{ cotizacion.razon_social }}{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Fecha:</span>
                            <span class="value">{{ cotizacion.fecha_creacion|date:"d/m/Y" }}</span>
                        </div>
                    </div>
                    <div class="info-card">
                        <h3>Información de Contacto</h3>
                        <div class="info-row">
                            <span class="label">Contacto:</span>
                            <span class="value">{% if cotizacion.contacto %}{{ cotizacion.contacto.nombres }} {{ cotizacion.contacto.apellidos }}{% else %}--{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Correo:</span>
                            <span class="value">{% if cotizacion.contacto %}{{ cotizacion.contacto.correo }}{% else %}--{% endif %}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Celular:</span>
                            <span class="value">{% if cotizacion.contacto %}{{ cotizacion.contacto.Celular }}{% else %}--{% endif %}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Tabla de Detalles -->
                <div class="details-section">
                    <table class="details-table">
                        <thead>
                            <tr>
                                <th style="width: 8%;">ITEM</th>
                                <th style="width: 50%;">DESCRIPCIÓN</th>
                                <th style="width: 12%;">UNIDAD</th>
                                <th style="width: 10%;">CANT.</th>
                                <th style="width: 12%;">P. UNIT.</th>
                                <th style="width: 12%;">SUBTOTAL</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for detalle in detalles %}
                            <tr>
                                <td>{{ forloop.counter }}</td>
                                <td class="description-cell">{{ detalle.descripcion }}</td>
                                <td>{{ detalle.unidad }}</td>
                                <td>{{ detalle.cantidad }}</td>
                                <td class="price-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ detalle.precio_unitario|floatformat:2 }}
                                </td>
                                <td class="price-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ detalle.precio_total|floatformat:2 }}
                                </td>
                            </tr>
                            {% endfor %}
                            <!-- Filas de totales mejoradas -->
                            <tr class="subtotal-row">
                                <td colspan="5" class="total-label-cell">SUBTOTAL</td>
                                <td class="total-amount-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ subtotal|floatformat:2 }}
                                </td>
                            </tr>
                            {% if cotizacion.incluye_igv %}
                            <tr class="igv-row">
                                <td colspan="5" class="total-label-cell">IGV (18%)</td>
                                <td class="total-amount-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ igv_monto|floatformat:2 }}
                                </td>
                            </tr>
                            {% endif %}
                            <tr class="total-row">
                                <td colspan="5" class="total-label-cell">TOTAL GENERAL</td>
                                <td class="total-amount-cell">
                                    {% if cotizacion.moneda == 'Soles' %}S/{% else %}${% endif %} {{ total_con_igv|floatformat:2 }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- MODIFICACIÓN 2: Nueva estructura de contenido -->
                <div class="bottom-section">
                    <div class="main-content-section">
                        <!-- Sección de Alcance (Izquierda) -->
                        <div class="scope-section">
                            <h3>Alcance de la Oferta</h3>
                            <div class="scope-content">
                                {{ cotizacion.alcance_total_oferta|linebreaks }}
                            </div>
                        </div>
                        
                        <!-- Información Lateral (Derecha) -->
                        <div class="right-info-section">
                            <!-- Cuentas Bancarias -->
                            <div class="bank-info-card">
                                <h4>Cuentas Bancarias</h4>
                                <p><span class="bank-account">INTERBANK SOLES</span></p>
                                <p>200-3003321671003-200-003003321671-31</p>
                                <p><span class="bank-account">INTERBANK DÓLARES</span></p>
                                <p>200-3007198016003-200-003007198016-30</p>
                                <p><span class="bank-account">DETRACCIÓN</span></p>
                                <p>00-059-144693</p>
                            </div>
                            
                            <!-- Términos -->
                            <div class="terms-card">
                                <div class="terms-content">
                                    <div class="terms-label">Validez de la Oferta</div>
                                    <div class="terms-value">{{ cotizacion.validez_oferta|default:"30 días" }}</div>
                                </div>
                                <div class="terms-content">
                                    <div class="terms-label">Forma de Pago</div>
                                    <div class="terms-value">{{ cotizacion.forma_pago|default:"AL CONTADO" }}</div>
                                </div>
                                <div class="terms-content">
                                    <div class="terms-label">Moneda</div>
                                    <div class="terms-value">{{ cotizacion.moneda|default:"Soles" }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Nota de Tipo de Cambio -->
                <div class="exchange-note">
                    {% if cotizacion.moneda == 'Dolares' %}
                        Para la conversión a soles, se empleará el tipo de cambio de S/ {{ tipo_cambio_efectivo|floatformat:3 }} (BCR + margen) vigente en la fecha de la cotización.
                    {% else %}
                        Precios expresados en {{ cotizacion.moneda|default:"Soles" }}.
                        {% if cotizacion.moneda == 'Soles' and tipo_cambio_efectivo %}
                            Tipo de cambio referencial USD: S/ {{ tipo_cambio_efectivo|floatformat:3 }}
                        {% endif %}
                    {% endif %}
                </div>
                
                <!-- Certificación -->
                <div class="certification">
                    <img src="https://www.cns.com.pe/wp-content/uploads/2021/12/HODELPE-1-HOMOLOGADO-POR-HODELPE-1-e1640187408664-300x295.jpg" alt="Certificación" class="cert-logo">
                    <div class="cert-text">Empresa certificada y homologada</div>
                </div>
            </div>
        </body>
        </html>
          """
          
        html_rendered = Template(plantilla_html).render(Context({
            'cotizacion': cotizacion,
            'detalles': cotizacion.detalles.all(),
            'subtotal': cotizacion.subtotal,
            'igv_monto': cotizacion.igv_monto,
            'total_con_igv': cotizacion.total_con_igv,
            'total_soles': cotizacion.total_soles,
            'total_dolares': cotizacion.total_dolares,
            'tipo_cambio_efectivo': cotizacion.tipo_cambio_efectivo,
            'user': request.user
        }))
          
        # Generar PDF usando gotenberg
        pdf_bytes = html_to_pdf_bytes_gotenberg(html_rendered)
        
        if not pdf_bytes:
            messages.error(request, 'No se pudo generar el PDF, revisar el servicio del PDF')
            return redirect('ventas:cotizaciones_list')
        
        # Retornar PDF para visualización en navegador (inline, no descarga)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="cotizacion_{cotizacion.numero_cotizacion}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error al generar el PDF: {str(e)}')
        return redirect('ventas:cotizaciones_list')


@login_required
def detalle_cotizacion(request, pk):
    """
    Vista para ver y editar los detalles de una cotización existente
    """
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    form_action = reverse('ventas:detalle_cotizacion', args=[cotizacion.pk])
    pdf_url = reverse('ventas:visualizar_pdf_cotizacion', args=[cotizacion.pk])
    contactos_url_template = reverse(
        'ventas:api_contactos_por_cliente',
        kwargs={'cliente_id': 999999}
    ).replace('999999', '{id}')

    def _build_context(form, detalles_formset):
        empty_form = detalles_formset.empty_form
        unidad_choices = list(empty_form.fields['unidad'].choices)

        moneda_actual = None
        if form.is_bound:
            moneda_actual = form.data.get(form.add_prefix('moneda'))
            if not moneda_actual and hasattr(form, 'cleaned_data'):
                moneda_actual = form.cleaned_data.get('moneda')
        if not moneda_actual:
            moneda_actual = form.initial.get('moneda') or cotizacion.moneda or 'Soles'

        moneda_simbolo = 'S/' if moneda_actual == 'Soles' else '$'

        # Registrar el contacto inicial en los atributos del widget para el JS
        contacto_initial = None
        if form.is_bound:
            contacto_initial = form.data.get(form.add_prefix('contacto'))
        if not contacto_initial:
            contacto_initial = form.initial.get('contacto') if form.initial else None
        if not contacto_initial and getattr(form.instance, 'contacto_id', None):
            contacto_initial = form.instance.contacto_id

        widget_attrs = form.fields['contacto'].widget.attrs
        if contacto_initial:
            widget_attrs['data-initial'] = str(contacto_initial)
        else:
            widget_attrs.pop('data-initial', None)

        return {
            'cotizacion': cotizacion,
            'form': form,
            'detalles_formset': detalles_formset,
            'form_action': form_action,
            'pdf_url': pdf_url,
            'contactos_url_template': contactos_url_template,
            'moneda_simbolo': moneda_simbolo,
            'unidad_choices': unidad_choices,
            'totales': {
                'subtotal': cotizacion.subtotal,
                'igv': cotizacion.igv_monto,
                'total': cotizacion.total_con_igv,
            },
        }
    
    if request.method == 'POST':
        # Manejar actualización de cotización
        form = CotizacionForm(request.POST, instance=cotizacion)
        detalles_formset = DetallesCotizacionesInLineFormSet(
            request.POST, 
            instance=cotizacion,
            prefix='detalles'
        )
        
        if form.is_valid() and detalles_formset.is_valid():
            # Actualizar la cotización
            cotizacion_actualizada = form.save(commit=False)
            
            # Actualizar tipo de cambio si es necesario
            if cotizacion_actualizada.moneda == 'Dolares':
                cotizacion_actualizada.actualizar_tipo_cambio()
            
            # Actualizar fecha de última modificación del estado
            if 'estado_coti' in form.changed_data:
                cotizacion_actualizada.fecha_actualizacion_estado = timezone.now()
            
            cotizacion_actualizada.save()
            
            # Guardar detalles
            detalles_formset.save()

            # Refrescar instancia
            cotizacion.refresh_from_db()
            
            # Si es una petición AJAX (modal), devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                payload = {
                    'success': True,
                    'message': 'Cotización actualizada correctamente',
                    'reload': True,
                }
                if 'generar_pdf' in request.POST:
                    payload['pdf_url'] = pdf_url
                return JsonResponse(payload)
            
            messages.success(request, 'Cotización actualizada correctamente.')
            
            # Si se solicita generar PDF
            if 'generar_pdf' in request.POST:
                return redirect('ventas:visualizar_pdf_cotizacion', pk=cotizacion.pk)
            
            return redirect('ventas:cotizaciones_list')
        else:
            context = _build_context(form, detalles_formset)
            # Si es una petición AJAX, devolver el formulario con errores
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string(
                    'cotizaciones/detalle_cotizacion_modal.html',
                    context,
                    request=request,
                )
                return JsonResponse({'success': False, 'html': html}, status=400)
            
            # Mostrar errores en página normal
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        # Mostrar formulario para edición
        form = CotizacionForm(instance=cotizacion)
        detalles_formset = DetallesCotizacionesInLineFormSet(
            instance=cotizacion,
            prefix='detalles'
        )
    
    context = _build_context(form, detalles_formset)

    # Si es petición AJAX (modal), usar template simplificado
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            return render(request, 'cotizaciones/detalle_cotizacion_modal.html', context)
        except Exception as e:
            # En caso de error, devolver respuesta JSON con el error
            return JsonResponse({
                'success': False, 
                'error': str(e),
                'message': 'Error al cargar el formulario de cotización'
            }, status=500)
    
    context['es_edicion'] = True
    return render(request, 'cotizaciones/detalle_cotizacion.html', context)
    # Por convención de Django (app templates), la ruta correcta es "cotizaciones/cotizaciones_dashboard.html"
    return render(request, 'cotizaciones/cotizaciones_dashboard.html', ctx)