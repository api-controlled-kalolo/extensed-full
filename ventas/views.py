from django.http import HttpResponse
from django.template import Template, Context
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from .forms import ActaServicioForm, EquiposActaInlineFormSet, AccionesActaLineFormSet
import pdfkit
from django.urls import reverse
from services.pdf_enginge import html_to_pdf_bytes_playwright
from services.gotenberg_engine import html_to_pdf_bytes_gotenberg 


from services.google_sheets import read_range, read_ranges, write_range, write_ranges, append_rows
from services.google_gas import subir_pdf_a_gas
import uuid

WKHTML_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Create your views here.

@login_required
def create_acta(request):
    #Solo se esta ingresando a la página
    if request.method == 'GET':
        return render(request,'actas/create_acta.html',{
            'form': ActaServicioForm(),
            'equipos': EquiposActaInlineFormSet(),
            'acciones': AccionesActaLineFormSet()
        })
    else: 
        try:
            print(request.POST)
            form = ActaServicioForm(request.POST)
            equipos = EquiposActaInlineFormSet(request.POST)
            acciones = AccionesActaLineFormSet(request.POST)
            
            # Validacion
            if form.is_valid():
                
                new_acta = form.save(commit=False)
                new_acta.save()
                
                equipos = EquiposActaInlineFormSet(request.POST, instance=new_acta)
                acciones = AccionesActaLineFormSet(request.POST, instance=new_acta)
                
                if equipos.is_valid() and acciones.is_valid():
                    equipos.save()
                    acciones.save()
                    
                    firma_tecnico_b64 = request.POST.get('firma_tecnico_b64')  # 'data:image/png;base64,...' o '' 
                    
                    plantilla_html = r"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="utf-8"/>
                        <title>Acta de Servicio Técnico</title>
                        <style>
                            /* Reset y configuración base */
                            * {
                                margin: 0;
                                padding: 0;
                                box-sizing: border-box;
                            }
                            
                            body {
                                font-family: Arial, sans-serif;
                                font-size: 9pt;
                                line-height: 1.2;
                                color: #000;
                                background: white;
                            }
                            
                            /* Contenedor principal */
                            .container {
                                padding: 15px;
                                max-width: 100%;
                            }
                            
                            /* Header principal */
                            .header {
                                text-align: center;
                                font-weight: bold;
                                margin-bottom: 20px;
                                position: relative;
                                border-bottom: 2px solid #000;
                                padding-bottom: 10px;
                            }
                            
                            .header .title {
                                font-size: 14pt;
                                text-transform: uppercase;
                            }
                            
                            .header .numero-acta {
                                position: absolute;
                                right: 0;
                                top: 0;
                                font-size: 10pt;
                            }
                            
                            /* Secciones */
                            .seccion-group {
                                border: 1px solid #000;
                                margin-bottom: 15px;
                                padding: 12px;
                                break-inside: avoid;
                            }
                            
                            .section-title {
                                font-weight: bold;
                                font-size: 10pt;
                                margin-bottom: 8px;
                                background-color: #f5f5f5;
                                padding: 5px;
                                border-left: 4px solid #000;
                            }
                            
                            .subsection-title {
                                font-weight: bold;
                                font-size: 9pt;
                                margin: 10px 0 8px 0;
                                padding: 3px 0;
                                border-bottom: 1px solid #ccc;
                            }
                            
                            /* Tablas */
                            .info-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 8pt;
                            }
                            
                            .info-table td {
                                padding: 3px 5px;
                                vertical-align: top;
                                border-bottom: 1px solid #ddd;
                            }
                            
                            .info-table td:first-child {
                                width: 15%;
                            }
                            
                            .info-table td:nth-child(2) {
                                width: 18%;
                            }
                            
                            .info-table td:nth-child(3) {
                                width: 12%;
                            }
                            
                            .info-table td:nth-child(4) {
                                width: 18%;
                            }
                            
                            .info-table td:nth-child(5) {
                                width: 12%;
                            }
                            
                            .info-table td:nth-child(6) {
                                width: 25%;
                            }
                            
                            /* Etiquetas de campos */
                            .field-label {
                                font-weight: bold;
                            }
                            
                            .field-value {
                                border-bottom: 1px solid #000;
                                min-height: 12px;
                                padding: 2px;
                            }
                            
                            /* Checkboxes */
                            .checkbox-group {
                                display: inline-block;
                                margin-right: 15px;
                                font-size: 8pt;
                            }
                            
                            .checkbox {
                                display: inline-block;
                                width: 10px;
                                height: 10px;
                                border: 1px solid #000;
                                margin-right: 3px;
                                vertical-align: middle;
                            }
                            
                            .checkbox.checked {
                                background-color: #000;
                            }
                            
                            /* Tabla de equipos */
                            .equipment-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 8pt;
                                margin-top: 8px;
                            }
                            
                            .equipment-table th,
                            .equipment-table td {
                                border: 1px solid #000;
                                padding: 4px 2px;
                                text-align: center;
                                vertical-align: middle;
                            }
                            
                            .equipment-table th {
                                background-color: #f5f5f5;
                                font-weight: bold;
                                font-size: 7pt;
                            }
                            
                            .equipment-table td {
                                font-size: 7pt;
                            }
                            
                            /* Anchos específicos para columnas de equipos */
                            .equipment-table th:nth-child(1),
                            .equipment-table td:nth-child(1) { width: 5%; }
                            .equipment-table th:nth-child(2),
                            .equipment-table td:nth-child(2) { width: 5%; }
                            .equipment-table th:nth-child(3),
                            .equipment-table td:nth-child(3) { width: 20%; }
                            .equipment-table th:nth-child(4),
                            .equipment-table td:nth-child(4) { width: 12%; }
                            .equipment-table th:nth-child(5),
                            .equipment-table td:nth-child(5) { width: 12%; }
                            .equipment-table th:nth-child(6),
                            .equipment-table td:nth-child(6) { width: 15%; }
                            .equipment-table th:nth-child(7),
                            .equipment-table td:nth-child(7) { width: 15%; }
                            .equipment-table th:nth-child(8),
                            .equipment-table td:nth-child(8) { width: 8%; }
                            .equipment-table th:nth-child(9),
                            .equipment-table td:nth-child(9) { width: 8%; }
                            
                            /* Tabla de materiales */
                            .materials-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 7pt;
                            }
                            
                            .materials-table td {
                                padding: 2px 3px;
                                vertical-align: top;
                                border-bottom: 1px solid #ddd;
                            }
                            
                            /* Tabla de información técnica */
                            .tech-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 8pt;
                            }
                            
                            .tech-table td {
                                padding: 5px;
                                vertical-align: top;
                                border: 1px solid #ddd;
                            }
                            
                            .tech-section {
                                border: 1px solid #000;
                                padding: 8px;
                                margin: 5px 0;
                            }
                            
                            /* Textarea personalizado */
                            .text-area {
                                width: 100%;
                                min-height: 60px;
                                border: 1px solid #000;
                                padding: 5px;
                                font-size: 8pt;
                                background-color: #fafafa;
                            }
                            
                            .text-area-small {
                                width: 100%;
                                min-height: 40px;
                                border: 1px solid #000;
                                padding: 3px;
                                font-size: 7pt;
                                background-color: #fafafa;
                            }
                            
                            /* Sección de conformidad */
                            .conformidad-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 8pt;
                            }
                            
                            .conformidad-table td {
                                padding: 8px;
                                border: 1px solid #000;
                                vertical-align: top;
                            }
                            
                            .satisfaccion-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 8pt;
                                margin-top: 10px;
                            }
                            
                            .satisfaccion-table th,
                            .satisfaccion-table td {
                                border: 1px solid #000;
                                padding: 5px;
                                text-align: center;
                            }
                            
                            .satisfaccion-table th {
                                background-color: #f5f5f5;
                                font-weight: bold;
                            }
                            
                            /* Preguntas de satisfacción */
                            .pregunta-satisfaccion {
                                margin: 10px 0;
                                padding: 5px 0;
                                border-bottom: 1px dotted #ccc;
                            }
                            
                            .respuesta-box {
                                display: inline-block;
                                width: 40px;
                                height: 20px;
                                border: 1px solid #000;
                                text-align: center;
                                margin: 0 5px;
                                vertical-align: middle;
                            }
                            
                            /* Sección de firmas */
                            .firmas-container {
                                display: table;
                                width: 100%;
                                margin-top: 20px;
                            }
                            
                            .firma-box {
                                display: table-cell;
                                width: 45%;
                                border: 1px solid #000;
                                padding: 15px;
                                text-align: center;
                                vertical-align: top;
                                margin: 0 2.5%;
                            }
                            
                            .firma-title {
                                font-weight: bold;
                                font-size: 9pt;
                                margin-bottom: 10px;
                            }
                            
                            .firma-field {
                                margin: 8px 0;
                                text-align: left;
                            }
                            
                            .firma-line {
                                border-bottom: 1px solid #000;
                                min-height: 20px;
                                margin: 5px 0;
                                display: inline-block;
                                width: 100%;
                            }
                            
                            .firma-image-area {
                                border: 1px solid #ccc;
                                min-height: 60px;
                                margin: 10px 0;
                                text-align: center;
                                padding: 5px;
                            }
                            
                            .firma-image-area img {
                                max-width: 100%;
                                max-height: 50px;
                            }
                            
                            /* Negación de firma */
                            .negacion-firma {
                                margin-top: 15px;
                                padding: 10px;
                                border: 1px solid #000;
                            }
                            
                            /* Disclaimer final */
                            .disclaimer {
                                margin-top: 20px;
                                padding: 15px;
                                border: 2px solid #000;
                                background-color: #f9f9f9;
                                font-size: 8pt;
                                text-align: justify;
                                font-weight: bold;
                            }
                            
                            /* Estilos específicos para celdas de información del cliente */
                            .cliente-info .info-table td {
                                border-right: 1px solid #ddd;
                            }
                            
                            .cliente-info .info-table td:last-child {
                                border-right: none;
                            }
                            
                            /* Celda especial para opciones complejas */
                            .complex-options {
                                border: 1px solid #ccc;
                                padding: 8px;
                                background-color: #fafafa;
                            }
                            
                            /* Utilidades */
                            .text-center {
                                text-align: center;
                            }
                            
                            .text-right {
                                text-align: right;
                            }
                            
                            .bold {
                                font-weight: bold;
                            }
                            
                            /* Ajustes para wkhtmltopdf */
                            @media print {
                                body {
                                    -webkit-print-color-adjust: exact;
                                }
                                
                                .container {
                                    padding: 10px;
                                }
                                
                                .seccion-group {
                                    margin-bottom: 10px;
                                    break-inside: avoid;
                                }
                                
                                .firmas-container {
                                    break-inside: avoid;
                                }
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <!-- Header -->
                            <div class="header">
                                <div class="title">Acta de Servicio Técnico</div>
                                <div class="numero-acta"><span class="bold">Nº</span> {{ acta.numero_acta }}</div>
                            </div>

                            <!-- Sección I: Información de la Orden -->
                            <div class="seccion-group">
                                <div class="section-title">I. INFORMACIÓN DE LA ORDEN</div>
                                <table class="info-table">
                                    <tr>
                                        <td class="field-label">Fecha:</td>
                                        <td class="field-value">{{ acta.fecha_acta|date:"Y-m-d" }}</td>
                                        <td class="field-label">SOT:</td>
                                        <td class="field-value">{{ acta.sot }}</td>
                                        <td class="field-label">Validación:</td>
                                        <td class="field-value">{{ acta.validacion }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Hora de inicio:</td>
                                        <td class="field-value">{{ acta.hora_inicio }}</td>
                                        <td class="field-label">Nº Cintillo:</td>
                                        <td class="field-value">{{ acta.numero_cintillo }}</td>
                                        <td class="field-label">FAT:</td>
                                        <td class="field-value">{{ acta.fat }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Hora de término:</td>
                                        <td class="field-value">{{ acta.hora_fin }}</td>
                                        <td class="field-label">Plano:</td>
                                        <td class="field-value">{{ acta.plano }}</td>
                                        <td class="field-label">Nº Borne FAT:</td>
                                        <td class="field-value">{{ acta.numero_borne_fat }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Plan:</td>
                                        <td class="field-value">{{ acta.Plan }}</td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Sección II: Información del Cliente -->
                            <div class="seccion-group cliente-info">
                                <div class="section-title">II. INFORMACIÓN DEL CLIENTE</div>
                                <table class="info-table">
                                    <tr>
                                        <td class="field-label">Razón Social / Nombres y Apellidos:</td>
                                        <td class="field-value">{{ acta.razon_social }}</td>
                                        <td class="field-label">Código de Cliente:</td>
                                        <td class="field-value">{{ acta.cod_cliente }}</td>
                                        <td class="field-label">Teléfono:</td>
                                        <td class="field-value">{{ acta.telefono }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Dirección:</td>
                                        <td class="field-value">{{ acta.direccion }}</td>
                                        <td class="field-label">Distrito:</td>
                                        <td class="field-value">{{ acta.distrito }}</td>
                                        <td class="field-label">Provincia:</td>
                                        <td class="field-value">{{ acta.provincia }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Persona que atendió al Personal Técnico:</td>
                                        <td class="complex-options" colspan="2">
                                            <div class="checkbox-group">
                                                {% if acta.titular %}✔{% else %}<span class="checkbox"></span>{% endif %} Titular
                                            </div>
                                            <div class="checkbox-group">
                                                {% if acta.usuario %}✔{% else %}<span class="checkbox"></span>{% endif %} Usuario
                                            </div>
                                            <br>
                                            <div class="checkbox-group">
                                                {% if acta.otros %}✔{% else %}<span class="checkbox"></span>{% endif %} Otros
                                            </div>
                                            <div style="margin-top: 5px;">
                                                <strong>Relación con el titular:</strong> {{ acta.relacion_titular }}
                                            </div>
                                        </td>
                                        <td class="field-label" colspan="2">¿El cliente brinda las facilidades para la instalación?</td>
                                        <td class="complex-options">
                                            <div class="checkbox-group">
                                                {% if acta.cliente_buena_brinda %}✔{% else %}<span class="checkbox"></span>{% endif %} Sí
                                            </div>
                                            <div class="checkbox-group">
                                                {% if acta.cliente_mala_brinda %}✔{% else %}<span class="checkbox"></span>{% endif %} No
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Sección III: Servicio Técnico -->
                            <div class="seccion-group">
                                <div class="section-title">III. SERVICIO TÉCNICO</div>
                                
                                <div class="subsection-title">3.1 PERSONAL TÉCNICO T1/T2 (NOMBRES Y APELLIDOS)</div>
                                <table class="info-table">
                                    <tr>
                                        <td class="field-label">T1 Líder:</td>
                                        <td class="field-value">{{ acta.t1_lider }}</td>
                                        <td class="field-label">T2 Apoyo:</td>
                                        <td class="field-value">{{ acta.t2_apoyo }}</td>
                                        <td class="field-label">T1/T2 Adicional:</td>
                                        <td class="field-value">{{ acta.t_adicional }}</td>
                                    </tr>
                                </table>
                                
                                <div class="subsection-title">3.2 PLATAFORMA (Aplica para residencias y Claro empresas)</div>
                                <table class="info-table">
                                    <tr>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.HFC %}✔{% else %}<span class="checkbox"></span>{% endif %} HFC
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.FTTH %}✔{% else %}<span class="checkbox"></span>{% endif %} FTTH
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.LTE %}✔{% else %}<span class="checkbox"></span>{% endif %} LTE
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.DTH %}✔{% else %}<span class="checkbox"></span>{% endif %} DTH
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.Otro %}✔{% else %}<span class="checkbox"></span>{% endif %} Otro: {{ acta.Otro_text }}
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <div class="subsection-title">3.3 SERVICIO REALIZADO</div>
                                <table class="info-table">
                                    <tr>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.instalacion %}✔{% else %}<span class="checkbox"></span>{% endif %} Instalación
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.post_venta %}✔{% else %}<span class="checkbox"></span>{% endif %} Post Venta
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.cambio_de_plan %}✔{% else %}<span class="checkbox"></span>{% endif %} Cambio de Plan
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.migracion %}✔{% else %}<span class="checkbox"></span>{% endif %} Migración
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.traslado_externo %}✔{% else %}<span class="checkbox"></span>{% endif %} Traslado Externo
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.traslado_interno %}✔{% else %}<span class="checkbox"></span>{% endif %} Traslado Interno
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.traslado_acometida %}✔{% else %}<span class="checkbox"></span>{% endif %} Traslado Acometida
                                            </div>
                                        </td>
                                        <td>
                                            <div class="checkbox-group">
                                                {% if acta.retiro %}✔{% else %}<span class="checkbox"></span>{% endif %} Retiro
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <div class="subsection-title">3.4 EQUIPOS INSTALADOS (I) O RETIRADOS (R)</div>
                                <table class="equipment-table">
                                    <thead>
                                        <tr>
                                            <th>I</th>
                                            <th>R</th>
                                            <th>Descripción</th>
                                            <th>Marca</th>
                                            <th>Modelo</th>
                                            <th>Serie</th>
                                            <th>MAC/PON</th>
                                            <th>UA</th>
                                            <th>Datos TV</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for equipo in equipos %}
                                        <tr>
                                            <td>{% if equipo.label_i %}✔{% else %}&nbsp;{% endif %}</td>
                                            <td>{% if equipo.label_r %}✔{% else %}&nbsp;{% endif %}</td>
                                            <td>{{ equipo.desc }}</td>
                                            <td>{{ equipo.marca }}</td>
                                            <td>{{ equipo.modelo }}</td>
                                            <td>{{ equipo.serie }}</td>
                                            <td>{{ equipo.mac_pon }}</td>
                                            <td>{{ equipo.ua }}</td>
                                            <td>{{ equipo.datos_tv }}</td>
                                        </tr>
                                        {% empty %}
                                        <!-- Filas vacías por defecto -->
                                        <tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
                                        <tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
                                        <tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                                
                                <div class="subsection-title">3.5 MATERIALES EMPLEADOS</div>
                                <table class="materials-table">
                                    <tr>
                                        <td class="field-label">Coaxial c/mens RG6:</td>
                                        <td class="field-value">{{ acta.Coaxial_c_mens_RG6 }}</td>
                                        <td class="field-label">Conector RJ11:</td>
                                        <td class="field-value">{{ acta.conector_rj11 }}</td>
                                        <td class="field-label">Control remoto:</td>
                                        <td class="field-value">{{ acta.control_remoto }}</td>
                                        <td class="field-label">Cable Fibra Drop:</td>
                                        <td>
                                            <div class="checkbox-group">{% if acta.cable_fibra_drop == '50M' %}✔{% else %}<span class="checkbox"></span>{% endif %} 50M</div>
                                            <div class="checkbox-group">{% if acta.cable_fibra_drop == '80M' %}✔{% else %}<span class="checkbox"></span>{% endif %} 80M</div>
                                            <div class="checkbox-group">{% if acta.cable_fibra_drop == '100M' %}✔{% else %}<span class="checkbox"></span>{% endif %} 100M</div>
                                            <div class="checkbox-group">{% if acta.cable_fibra_drop == '150M' %}✔{% else %}<span class="checkbox"></span>{% endif %} 150M</div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Coaxial s/mens RG6:</td>
                                        <td class="field-value">{{ acta.Coaxial_s_mens_RG6 }}</td>
                                        <td class="field-label">Conector RJ45:</td>
                                        <td class="field-value">{{ acta.conector_rj45 }}</td>
                                        <td class="field-label">Cable HDMI:</td>
                                        <td class="field-value">{{ acta.cable_hdmi }}</td>
                                        <td class="field-label">Divisor:</td>
                                        <td>
                                            <div class="checkbox-group">{% if acta.divisor == '2v' %}✔{% else %}<span class="checkbox"></span>{% endif %} 2V</div>
                                            <div class="checkbox-group">{% if acta.divisor == '3v' %}✔{% else %}<span class="checkbox"></span>{% endif %} 3V</div>
                                            <div class="checkbox-group">{% if acta.divisor == '4V' %}✔{% else %}<span class="checkbox"></span>{% endif %} 4V</div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Cable telefónico:</td>
                                        <td class="field-value">{{ acta.cable_telefonico }}</td>
                                        <td class="field-label">Conector RG6:</td>
                                        <td class="field-value">{{ acta.conector_rg6 }}</td>
                                        <td class="field-label">Roseta Telef.:</td>
                                        <td class="field-value">{{ acta.roseta_telef }}</td>
                                        <td class="field-label">Otros:</td>
                                        <td class="field-value">{{ acta.otros_material }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Cable UTP:</td>
                                        <td class="field-value">{{ acta.cable_utp }}</td>
                                        <td class="field-label">Conector OPT:</td>
                                        <td class="field-value">{{ acta.conector_opt }}</td>
                                        <td class="field-label">Roseta Óptica:</td>
                                        <td class="field-value">{{ acta.roseta_optica }}</td>
                                        <td class="field-label">Grapas de pared:</td>
                                        <td class="field-value">{{ acta.grapas_pared }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Cable SC/APC:</td>
                                        <td class="field-value">{{ acta.cable_sc_APC }}</td>
                                        <td class="field-label">Anclaje P:</td>
                                        <td class="field-value">{{ acta.anclaje_p }}</td>
                                        <td class="field-label">Chapa Q:</td>
                                        <td class="field-value">{{ acta.chapa_q }}</td>
                                    </tr>
                                    <tr>
                                        <td class="field-label">Cinta aislante:</td>
                                        <td class="field-value">{{ acta.cinta_aislante }}</td>
                                        <td class="field-label">Cinta doble contacto:</td>
                                        <td class="field-value">{{ acta.cinta_doble_contacto }}</td>
                                        <td class="field-label">Alcohol isopropílico:</td>
                                        <td class="field-value">{{ acta.alcohol_isopropilico }}</td>
                                        <td class="field-label">Paños secos:</td>
                                        <td class="field-value">{{ acta.panos_secos }}</td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Sección IV: Información Técnica -->
                            <div class="seccion-group">
                                <div class="section-title">IV. INFORMACIÓN TÉCNICA</div>
                                <table class="tech-table">
                                    <tr>
                                        <td class="tech-section">
                                            <div class="subsection-title">1. NIVELES</div>
                                            <table class="info-table">
                                                <tr>
                                                    <td class="field-label">Down Stream/Rx ONT:</td>
                                                    <td class="field-value">{{ acta.down_stream_rx_ont }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">Up Stream/Tx ONT:</td>
                                                    <td class="field-value">{{ acta.up_stream_tx_ont }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">SINR</td>
                                                    <td class="field-value">{{ acta.sinr }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">RSRP</td>
                                                    <td class="field-value">{{ acta.rsrp }}</td>
                                                </tr>
                                            </table>
                                        </td>
                                        <td class="tech-section">
                                            <div class="subsection-title">2. SVA</div>
                                            <table class="info-table">
                                                <tr>
                                                    <td class="field-label">Hunting:</td>
                                                    <td class="field-value">{{ acta.hunting }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">Central virtual:</td>
                                                    <td class="field-value">{{ acta.central_virtual }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">IP Fija:</td>
                                                    <td class="field-value">{{ acta.ip_fija }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">Port Forwarding:</td>
                                                    <td class="field-value">{{ acta.post_forwarding }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">IP:</td>
                                                    <td class="field-value">{{ acta.ip_text }}</td>
                                                </tr>
                                            </table>
                                        </td>
                                        <td class="tech-section">
                                            <div class="subsection-title">3. WIFI</div>
                                            <table class="info-table">
                                                <tr>
                                                    <td class="field-label">SSID_2_4_GHZ:</td>
                                                    <td class="field-value">{{ acta.SSID_2_4_GHZ }}</td>
                                                </tr>
                                                <tr>
                                                    <td class="field-label">SSID_5_GHZ:</td>
                                                    <td class="field-value">{{ acta.SSID_5_GHZ }}</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Sección V: Mantenimiento/Reclamo -->
                            <div class="seccion-group">
                                <div class="section-title">V. LLENAR SOLO EN CASO DE MANTENIMIENTO / RECLAMO POR CALIDAD (OBLIGATORIO)</div>
                                
                                <div class="subsection-title">5.1 INCONVENIENTE</div>
                                <div class="text-area">{{ acta.incoveniente_texto|default:"" }}</div>
                                
                                <table class="info-table" style="margin-top: 10px;">
                                    <tr>
                                        <td style="width: 50%;">
                                            <div class="subsection-title">5.2 ACCIONES REALIZADAS PARA ATENDER EL INCONVENIENTE</div>
                                            <table class="equipment-table">
                                                <thead>
                                                    <tr>
                                                        <th>Código</th>
                                                        <th>Acciones</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {% for accion in acciones %}
                                                    <tr>
                                                        <td>{{ accion.codigo }}</td>
                                                        <td>{{ accion.acciones_text }}</td>
                                                    </tr>
                                                    {% empty %}
                                                    <tr><td>&nbsp;</td><td>&nbsp;</td></tr>
                                                    <tr><td>&nbsp;</td><td>&nbsp;</td></tr>
                                                    <tr><td>&nbsp;</td><td>&nbsp;</td></tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </td>
                                        <td style="width: 50%; vertical-align: top;">
                                            <div class="subsection-title">5.3 ¿EL INCONVENIENTE SE PUDO SOLUCIONAR?</div>
                                            <div style="margin: 10px 0;">
                                                <div class="checkbox-group">
                                                    {% if acta.incoveniente_solucionado == 'SI' %}✔{% else %}<span class="checkbox"></span>{% endif %} Sí
                                                </div>
                                                <div class="checkbox-group">
                                                    {% if acta.incoveniente_solucionado == 'NO' %}✔{% else %}<span class="checkbox"></span>{% endif %} No
                                                </div>
                                            </div>
                                            <div class="field-label" style="margin-top: 15px;">
                                                Indicar por qué NO se pudo solucionar y si se debe a causas ajenas a CLARO:
                                            </div>
                                            <div class="text-area-small">{{ acta.indicar_porque|default:"" }}</div>
                                        </td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Sección VI: Comentarios y Observaciones -->
                            <div class="seccion-group">
                                <div class="section-title">VI. COMENTARIOS Y OBSERVACIONES DEL SERVICIO (LLENADO POR EL PERSONAL TÉCNICO)</div>
                                <div class="text-area">{{ acta.comentarios_texto|default:"" }}</div>
                            </div>

                            <!-- Sección VII: Firmas -->
                            <div class="seccion-group">
                                <div class="section-title">VII. FIRMAS</div>
                                
                                <div class="firmas-container">
                                    <div class="firma-box">
                                        <div class="firma-title">TÉCNICO</div>
                                        <div class="firma-field">
                                            <span class="field-label">Nombre:</span><br>
                                            <div class="firma-line">{{ acta.nombre_tecnico|default:"" }}</div>
                                        </div>
                                        <div class="firma-field">
                                            <span class="field-label">DNI:</span><br>
                                            <div class="firma-line">{{ acta.dni_tecnico|default:"" }}</div>
                                        </div>
                                        <div class="firma-field">
                                            <span class="field-label">Firma:</span>
                                            <div class="firma-image-area">
                                                {% if firma_tecnico_b64 %}
                                                    <img src="{{ firma_tecnico_b64 }}" alt="Firma del Técnico">
                                                {% else %}
                                                    &nbsp;
                                                {% endif %}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Disclaimer legal -->
                            <div class="disclaimer">
                                Claro no es responsable por fallas, daños o desperfectos en los dispositivos y/o equipos propiedad del cliente (Televisor, Teléfono, Computadora, Reproductores de video, consolas de video juegos, entre otros), derivados por manipulación por parte del cliente o terceros o en los casos en que el cliente no hubiese estado en la diligencia debida en su custodia y mantenimiento.
                            </div>

                        </div>
                    </body>
                    </html>
                    """
                    html_rendered = Template(plantilla_html).render(Context({'acta': new_acta, 'equipos': new_acta.equipos.all(), 'acciones': new_acta.acciones.all(),'firma_tecnico_b64': firma_tecnico_b64,}))
                    
                    # Convertir a PDF
                    pdf_bytes = html_to_pdf_bytes_gotenberg(html_rendered)
                    if not pdf_bytes:
                        return render(request, 'actas/create_acta.html', {
                            'form': ActaServicioForm(),
                            'error': 'No se pudo generar el PDF (wkhtmltopdf). Revisa el HTML/CSS o el binario.'
                        })
                    # DESCARGA AUTOMÁTICA (sin previsualización)
                    response = HttpResponse(pdf_bytes,content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="acta_{new_acta.pk}.pdf"'
                    
                    print("PDF generado con exito")
                    
                    # === Subir a Drive ===
                    nombre_pdf = f"acta_{new_acta.pk}.pdf"
                    drive_link = ""
                    try:
                        res = subir_pdf_a_gas(pdf_bytes, nombre_pdf)
                        drive_link = res.get("webViewLink") or res.get("url")
                        print("Subido vía Apps Script:", drive_link)
                    except Exception as e:
                        print("ERROR subiendo via Apps Scripts: ", repr(e))
                        drive_link = ""
                        
                    # === Registrar en Sheets ===
                    SPREADSHEET_ID = "1WMIl8f4KTsj_DvGpXIhFe9Mn7aRNKYp2CsPb0zERT_Q"
                    
                    fecha_str = str(new_acta.fecha_acta)

                    try:
                        
                        # Actualizando Hoja Principal - HOJA 'ACTAS'
                        codigo_unico = str(uuid.uuid4())
                        rows = [[
                                codigo_unico,
                                f"{new_acta.numero_acta}",
                                fecha_str,
                                f"{new_acta.cod_cliente}",
                                f"{new_acta.razon_social}",
                                f'=HYPERLINK("{drive_link}"; "Ver PDF")' if drive_link else "",
                                f"{new_acta.hora_inicio}" if new_acta.hora_inicio else "",
                                f"{new_acta.hora_fin}" if new_acta.hora_fin else "",
                                f"{new_acta.sot}",
                                f"{new_acta.numero_cintillo}",
                                f"{new_acta.plano}" if new_acta.plano else "",
                                f"{new_acta.validacion}",
                                f"{new_acta.fat}" if new_acta.fat else "",
                                f"{new_acta.numero_borne_fat}",
                                f"{new_acta.telefono}" if new_acta.telefono else "",
                                f"{new_acta.provincia}" if new_acta.provincia else "",
                                f"{new_acta.distrito}" if new_acta.distrito else "",
                                f"{'✓' if new_acta.titular else ''}",
                                f"{'✓' if new_acta.otros else ''}",
                                f"{'✓' if new_acta.usuario else ''}",
                                f"{new_acta.relacion_titular}" if new_acta.relacion_titular else "",
                                f"{'✓' if new_acta.cliente_buena_brinda else ''}",
                                f"{new_acta.t1_lider}" if new_acta.t1_lider else "",
                                f"{new_acta.t2_apoyo}" if new_acta.t2_apoyo else "",
                                f"{new_acta.t_adicional}" if new_acta.t_adicional else "",
                                f"{'✓' if new_acta.HFC else ''}",
                                f"{'✓' if new_acta.FTTH else ''}",
                                f"{'✓' if new_acta.LTE else ''}",
                                f"{'✓' if new_acta.DTH else ''}",
                                f"{'✓' if new_acta.Otro else ''}",
                                f"{new_acta.Otro_text}" if new_acta.Otro_text else "",
                                f"{new_acta.Plan}" if new_acta.Plan else "",
                                f"{'✓' if new_acta.instalacion else ''}",
                                f"{'✓' if new_acta.post_venta else ''}",
                                f"{'✓' if new_acta.mantenimiento_atencionReclamo_Calidad else ''}",
                                f"{'✓' if new_acta.retiro else ''}",
                                f"{'✓' if new_acta.retiro_acometida else ''}",
                                f"{new_acta.Coaxial_c_mens_RG6}",
                                f"{new_acta.Coaxial_s_mens_RG6}",
                                f"{new_acta.cable_telefonico}",
                                f"{new_acta.cable_utp}",
                                f"{new_acta.cable_sc_APC}",
                                f"{new_acta.conector_rj11}",
                                f"{new_acta.conector_rj45}",
                                f"{new_acta.conector_rg6}",
                                f"{new_acta.conector_opt}",
                                f"{new_acta.anclaje_p}",
                                f"{new_acta.control_remoto}",
                                f"{new_acta.cable_hdmi}",
                                f"{new_acta.roseta_telef}",
                                f"{new_acta.roseta_optica}",
                                f"{new_acta.cable_fibra_drop}" if new_acta.cable_fibra_drop else "" ,
                                f"{new_acta.divisor}" if new_acta.divisor else "" ,
                                f"{new_acta.otros_material}" if new_acta.otros_material else "" ,
                                f"{new_acta.grapas_pared}",
                                f"{new_acta.cinta_aislante}",
                                f"{new_acta.cinta_doble_contacto}",
                                f"{new_acta.alcohol_isopropilico}",
                                f"{new_acta.panos_secos}",
                                f"{new_acta.otros_material2}" if new_acta.otros_material2 else "" ,
                                f"{new_acta.down_stream_rx_ont}" if new_acta.down_stream_rx_ont else "",
                                f"{new_acta.up_stream_tx_ont}" if new_acta.up_stream_tx_ont else "",
                                f"{new_acta.sinr}" if new_acta.sinr else "",
                                f"{new_acta.rsrp}" if new_acta.rsrp else "",
                                f"{'✓' if new_acta.hunting else ''}",
                                f"{'✓' if new_acta.ip_fija else ''}",
                                f"{'✓' if new_acta.central_virtual else ''}",
                                f"{'✓' if new_acta.post_forwarding else ''}",
                                f"{new_acta.ip_text}" if new_acta.ip_text else "",
                                f"{new_acta.SSID_2_4_GHZ}" if new_acta.SSID_2_4_GHZ else "",
                                f"{new_acta.SSID_5_GHZ}" if new_acta.SSID_5_GHZ else "",
                                f"{new_acta.incoveniente_texto}" if new_acta.incoveniente_texto else "",
                                f"{new_acta.incoveniente_solucionado}" if new_acta.incoveniente_solucionado else "",
                                f"{new_acta.indicar_porque}" if new_acta.indicar_porque else "",
                                f"{new_acta.comentarios_texto}" if new_acta.comentarios_texto else "",
                                f"{new_acta.nombre_cliente}" if new_acta.nombre_cliente else "",
                                f"{new_acta.dni_cliente}" if new_acta.dni_cliente else "",
                                f"{'✓' if new_acta.el_cliente_nego_acta else ''}",
                                f"{new_acta.motivo_texto}" if new_acta.motivo_texto else "",
                            ]
                        ]

                        updated_cells = append_rows(
                            SPREADSHEET_ID,
                            "'ACTAS'!A:ZZ",  # ahora hay 4 columnas
                            rows,
                            value_input="USER_ENTERED"   # para que la fórmula HYPERLINK se interprete
                        )
                        print(f"Fila enviada (updated_cells={updated_cells})")
                        
                        # Actualizando Hoja Principal - HOJA 'ACTAS_EQUIPOS'
                        
                        # --- EQUIPOS ---
                        equipos_array = []
                        EQUIPOS_FIELDS = ["label_i", "label_r", "desc", "marca", "modelo", "serie", "mac_pon", "ua", "datos_tv"]

                        for form in equipos:  # o equipos.forms
                            cd = getattr(form, "cleaned_data", None)
                            if not cd or cd.get("DELETE"):
                                continue
                            fila = [codigo_unico, new_acta.numero_acta] + [(cd.get(f) or "") for f in EQUIPOS_FIELDS]
                            equipos_array.append(fila)

                        if equipos_array:  # evita llamada vacía
                            equipos_updated_cells = append_rows(
                                SPREADSHEET_ID,
                                "'EQUIPOS_ACTAS'!A:ZZ",
                                equipos_array,
                                value_input="RAW"  # o "USER_ENTERED" si prefieres
                            )
                            print(f"Filas enviadas (equipos_updated_cells={equipos_updated_cells})")

                        # --- ACCIONES ---
                        acciones_array = []
                        ACCIONES_FIELDS = ["codigo", "acciones_text"]

                        for form in acciones:
                            cd = getattr(form, "cleaned_data", None)
                            if not cd or cd.get("DELETE"):
                                continue
                            fila = [codigo_unico, new_acta.numero_acta] + [(cd.get(f) or "") for f in ACCIONES_FIELDS]
                            acciones_array.append(fila)

                        if acciones_array:
                            acciones_updated_cells = append_rows(
                                SPREADSHEET_ID,
                                "'ACCIONES_ACTAS'!A:ZZ",
                                acciones_array,
                                value_input="RAW"
                            )
                            print(f"Filas enviadas (acciones_updated_cells={acciones_updated_cells})")
                        
                    except Exception as e:
                        print("ERROR al enviar fila a Google Sheets:", repr(e))
                    
                    return response
                else:
                     # Errores en el formset (tabla equipos)
                    campos_con_error = []
                    for f in equipos:
                        for c in f.errors.keys():
                            campos_con_error.append(c)
                    mensaje_error = "Hay errores en la tabla de equipos: " + ", ".join(set(campos_con_error)) if campos_con_error else "Hay errores en la tabla de equipos."
                    return render(request, 'actas/create_acta.html', {
                        'form': form,                 # mantenemos datos del acta ingresados
                        'equipos': equipos,           # formset con errores para que el usuario corrija
                        'error': mensaje_error,
                        'acciones': acciones,
                    })
            # Error en la validacion, los campos no fueron completados
            else:
                campos_con_error = [form.fields[c].label or c for c in form.errors.keys()]
                mensaje_error = "Hay un error en los campos siguientes: " + ", ".join(campos_con_error)
                return render(request,'actas/create_acta.html',{
                    'form': form,
                    'equipos': equipos,
                    'error': mensaje_error,
                    'acciones': acciones
                } )
        except ValueError as e:
            return render(request,'actas/create_acta.html',{
                'form': form,
                'equipos': equipos,
                'error': f"Hay un error en el Sistema {str(e)}",
                'acciones': acciones,
            })

# Helper: HTML -> PDF (bytes)
def html_to_pdf_bytes_wkhtml(html: str) -> bytes | None:
    try:
        wkhtml = WKHTML_PATH
        config = pdfkit.configuration(wkhtmltopdf=wkhtml) if wkhtml else None
        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'print-media-type': None
        }
        return pdfkit.from_string(html, False, options=options, configuration=config)
    except Exception:
        return None