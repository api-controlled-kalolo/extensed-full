from django import forms
from django.forms import inlineformset_factory
from .models import (
    ActaServicioTecnico,
    Equipos_ActaServicioTecnico,
    Acciones_ActaServicioTecnico,
    Cotizacion,
    Detalles_Cotizacion,
    Cliente,
    Contacto,
    UnidadNegocio,
    Proyecto
)
from ventas.utils.ubigeo import (
    ensure_district_matches_province,
    find_district_value,
    find_province_value,
    get_district_choices,
    get_province_choices,
    is_valid_district_value,
    is_valid_province_value,
    parse_district_value,
    parse_province_value,
)

# -- Actas --
class ActaServicioForm(forms.ModelForm):
    t1_lider = forms.ChoiceField(label='Líder', required=True)
    t2_apoyo = forms.ChoiceField(label='Apoyo', required=True)
    t_adicional = forms.ChoiceField(label='Técnico Adicional', required=False)
    class Meta:
        model = ActaServicioTecnico
        # Colocamos todo menos el campo 'numero_acta'
        exclude = ['numero_acta']
        widgets = {
            'fecha_acta': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),
            'hora_inicio': forms.TimeInput(
                attrs={
                    'type': 'time'
                }
            ),
            'hora_fin': forms.TimeInput(
                attrs = {
                    'type': 'time'
                }
            ),
        }
    def __init__(self, *args, choices_t1=None, choices_t2=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegura widget <select>
        self.fields["t1_lider"].widget = forms.Select()
        self.fields["t2_apoyo"].widget = forms.Select()
        self.fields["t_adicional"].widget = forms.Select()

        # Placeholders + choices
        c1 = [("", "— Selecciona —")] + (choices_t1 or [])
        c2 = [("", "— Selecciona —")] + (choices_t2 or [])

        self.fields["t1_lider"].choices = c1
        self.fields["t2_apoyo"].choices = c2
        # “Adicional” opcional
        self.fields["t_adicional"].choices = [("", "— Ninguno —")] + (choices_t2 or [])
        self.fields["t_adicional"].required = False

class Equipos_ActaServicioForm(forms.ModelForm):
    class Meta:
        model = Equipos_ActaServicioTecnico
        fields = ['label_i', 'label_r', 'desc', 'marca', 'modelo', 'serie', 'mac_pon', 'ua', 'datos_tv']

class Acciones_ActaServicioForm(forms.ModelForm):
    class Meta:
        model = Acciones_ActaServicioTecnico
        fields = ['codigo', 'acciones_text']

EquiposActaInlineFormSet = inlineformset_factory(
    parent_model=ActaServicioTecnico,
    model=Equipos_ActaServicioTecnico,
    form=Equipos_ActaServicioForm,
    extra=7,                 # ← 7 formularios vacíos de arranque
    can_delete=True,         # permitir marcar para borrar
    max_num=50,              # límite de formularios si querés
    validate_max=True
)

AccionesActaLineFormSet = inlineformset_factory(
    parent_model = ActaServicioTecnico,
    model= Acciones_ActaServicioTecnico,
    form = Acciones_ActaServicioForm,
    extra=5,                 # ← 5 formularios vacíos de arranque
    can_delete=True,         # permitir marcar para borrar
    max_num=50,              # límite de formularios si querés
    validate_max=True
)

# -- Cotizaciones --
class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        # Colocamos todo menos los campos que se van a completar automáticamente:
        exclude = [
            'numero_cotizacion', 'ruc', 'razon_social', 'fecha_creacion', 
            'tipo_cambio', 'fecha_actualizacion_estado'
        ]
        widgets = {
            'nombre_cotizacion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre de la cotización'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Se llenará automáticamente',
                'readonly': 'readonly',
                'style': 'background-color: #f8f9fa;'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Se llenará automáticamente',
                'readonly': 'readonly',
                'style': 'background-color: #f8f9fa;'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Se llenará automáticamente',
                'readonly': 'readonly',
                'style': 'background-color: #f8f9fa;'
            }),
            'forma_pago': forms.Select(attrs={
                'class': 'form-select'
            }),
            'validez_oferta': forms.Select(attrs={
                'class': 'form-select'
            }),
            'moneda': forms.Select(attrs={
                'class': 'form-select'
            }),
            'incluye_igv': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'estado_coti': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alcance_total_oferta': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Detalle del alcance...', 
                'rows': 4
            }),
        }

    # Mostrar cliente/contacto como selects (FKs en el modelo)
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.none(), required=True, label='Cliente', widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_cliente'}))
    contacto = forms.ModelChoiceField(queryset=Contacto.objects.none(), required=True, label='Contacto', widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_contacto'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar labels personalizados
        self.fields['forma_pago'].label = 'Forma de Pago'
        self.fields['validez_oferta'].label = 'Validez de la Oferta'
        self.fields['moneda'].label = 'Moneda'
        self.fields['incluye_igv'].label = '¿Incluye IGV?'
        self.fields['estado_coti'].label = 'Estado de la Cotización'
        self.fields['alcance_total_oferta'].label = 'Alcance Total de la Oferta'
        self.fields['direccion'].label = 'Dirección del Cliente'
        self.fields['correo'].label = 'Correo del Contacto'
        self.fields['celular'].label = 'Celular del Contacto'
        
        # siempre todos los clientes
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('razon_social')

        # por defecto, contactos vacío hasta que se seleccione un cliente
        self.fields['contacto'].queryset = Contacto.objects.none()

        # Si hay data del formulario (POST) y se envió cliente, filtrar contactos
        data = getattr(self, 'data', None)
        cliente_selected = None
        if data and data.get(self.add_prefix('cliente')):
            try:
                cliente_selected = int(data.get(self.add_prefix('cliente')))
            except (TypeError, ValueError):
                cliente_selected = None
        # Si es edición y no hay POST, tomar de instance
        if not cliente_selected and getattr(self, 'instance', None) and getattr(self.instance, 'cliente_id', None):
            cliente_selected = self.instance.cliente_id

        if cliente_selected:
            self.fields['contacto'].queryset = Contacto.objects.filter(
                cliente_principal_id=cliente_selected
            ).order_by('nombres', 'apellidos')

        # labels para selects
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.razon_social} ({obj.ruc})"
        self.fields['contacto'].label_from_instance = lambda obj: f"{obj.nombres} {obj.apellidos} - {obj.cargo}"
    
    def save(self, commit=True):
        """Override save para auto-completar RUC, Razón Social, Dirección, Correo y Celular"""
        instance = super().save(commit=False)
        
        # Auto-completar desde Cliente
        if instance.cliente:
            instance.ruc = instance.cliente.ruc
            instance.razon_social = instance.cliente.razon_social
            instance.direccion = instance.cliente.direccion
        
        # Auto-completar desde Contacto
        if instance.contacto:
            instance.correo = instance.contacto.correo
            instance.celular = instance.contacto.Celular
        
        if commit:
            instance.save()
        
        return instance

class Detalles_CotizacionForms(forms.ModelForm):
    class Meta:
        model = Detalles_Cotizacion
        # Colocamos todo menos lo campos que se van a completar en automático:
        exclude = ['cotizacion_principal']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detalle de la partida, insumo o servicio',
                'rows': 3
            }),
            'unidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 300,
                'step': 1,
                'placeholder': 'Cantidad'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Precio unitario'
            }),
        }
        
DetallesCotizacionesInLineFormSet = inlineformset_factory(
    parent_model=Cotizacion,
    model=Detalles_Cotizacion,
    form=Detalles_CotizacionForms,
    extra=2,                 # ← 2 formularios vacíos de arranque
    can_delete=True,         # permitir marcar para borrar
    max_num=50,              # límite de formularios si querés
    validate_max=True
)

# -- Clientes -- 

class ClienteForm(forms.ModelForm):
    provincia = forms.ChoiceField(
        label='Provincia',
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    distrito = forms.ChoiceField(
        label='Distrito',
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    proyecto_principal = forms.ModelChoiceField(
        queryset=Proyecto.objects.select_related('unidad_negocio_principal').order_by('nombre'),
        required=True,
        label='Proyecto',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Cliente
        fields = ['proyecto_principal', 'ruc', 'razon_social', 'direccion', 'provincia', 'distrito']
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC', 'pattern': r'\d{11}', 'title': 'RUC de 11 dígitos'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón social'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proyecto_principal'].empty_label = 'Seleccione un Proyecto'
        # Texto visible en el dropdown: PROYECTO — [UN-CÓDIGO · UN-NOMBRE]
        self.fields['proyecto_principal'].label_from_instance = \
            (lambda obj: f"{obj.nombre} — [{obj.unidad_negocio_principal.codigo} · {obj.unidad_negocio_principal.nombre}]")

        # Provincias (ordenadas por departamento y nombre)
        province_choices = [('','Seleccione una provincia')] + get_province_choices()
        self.fields['provincia'].choices = province_choices

        province_field_name = self.add_prefix('provincia')
        district_field_name = self.add_prefix('distrito')

        # Determinar el value seleccionado para la provincia
        province_value = None
        if self.data and self.data.get(province_field_name):
            province_candidate = self.data.get(province_field_name)
            if is_valid_province_value(province_candidate):
                province_value = province_candidate
        else:
            initial_province = self.initial.get('provincia') or getattr(self.instance, 'provincia', '')
            province_value = find_province_value(initial_province)

        if province_value:
            self.fields['provincia'].initial = province_value

        # Determinar distritos en función de la provincia
        district_choices = []
        district_value = None
        if province_value:
            district_choices = get_district_choices(province_value)
            if self.data and self.data.get(district_field_name):
                district_candidate = self.data.get(district_field_name)
                if ensure_district_matches_province(province_value, district_candidate):
                    district_value = district_candidate
            else:
                initial_district = self.initial.get('distrito') or getattr(self.instance, 'distrito', '')
                district_value = find_district_value(province_value, initial_district)

        self.fields['distrito'].choices = [('','Seleccione un distrito')] + district_choices
        if district_value:
            self.fields['distrito'].initial = district_value

        # Guardamos el valor crudo para usarlo en clean_distrito
        self._province_value_raw = province_value

    def clean_provincia(self):
        value = self.cleaned_data.get('provincia')
        if not value:
            raise forms.ValidationError('Seleccione una provincia válida.')
        if not is_valid_province_value(value):
            raise forms.ValidationError('La provincia seleccionada no es válida.')
        # Guardamos para validar el distrito posteriormente
        self._province_value_raw = value
        _, province_name = parse_province_value(value)
        return province_name

    def clean_distrito(self):
        value = self.cleaned_data.get('distrito')
        if not value:
            raise forms.ValidationError('Seleccione un distrito válido.')
        if not is_valid_district_value(value):
            raise forms.ValidationError('El distrito seleccionado no es válido.')

        province_value = getattr(self, '_province_value_raw', None)
        if not province_value:
            # Intentamos recuperar desde los datos del formulario (en caso de error previo)
            province_candidate = self.data.get(self.add_prefix('provincia'))
            if province_candidate and is_valid_province_value(province_candidate):
                province_value = province_candidate

        if not province_value or not ensure_district_matches_province(province_value, value):
            raise forms.ValidationError('El distrito no pertenece a la provincia seleccionada.')

        _, _, district_name = parse_district_value(value)
        return district_name


class ContactoForm(forms.ModelForm):
    # Combo de clientes (con Proyecto y UN visibles)
    cliente_principal = forms.ModelChoiceField(
        queryset=Cliente.objects.select_related(
            'proyecto_principal__unidad_negocio_principal'
        ).order_by('razon_social'),
        required=True,
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Contacto
        fields = ['cliente_principal', 'apellidos', 'nombres', 'cargo', 'correo', 'Celular', 'Sede']
        widgets = {
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'Celular': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Celular (9 dígitos)',
                'maxlength': '9', 'pattern': r'\d{9}', 'title': 'Ingrese 9 dígitos',
                'inputmode': 'numeric'
            }),
            'Sede': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sede'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente_principal'].empty_label = 'Seleccione un Cliente'
        # Texto visible en el dropdown: Cliente — Proyecto [UN]
        def _label(c):
            pj = getattr(c, 'proyecto_principal', None)
            if pj and getattr(pj, 'unidad_negocio_principal', None):
                un = pj.unidad_negocio_principal
                return f"{c.razon_social} ({c.ruc}) — {pj.nombre} [{un.codigo} · {un.nombre}]"
            return f"{c.razon_social} ({c.ruc})"
        self.fields['cliente_principal'].label_from_instance = _label

    # Validación adicional del celular (opcional, pero útil)
    def clean_Celular(self):
        cel = self.cleaned_data.get('Celular', '').strip().replace(' ', '')
        if not cel.isdigit() or len(cel) != 9:
            raise forms.ValidationError('Ingrese un número de 9 dígitos.')
        return cel

# -- Unidad Negocio
class UnidadNegocioForm(forms.ModelForm):
    class Meta:
        model = UnidadNegocio
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la UN'})
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('Ingresa un nombre válido para la unidad de negocio.')

        qs = UnidadNegocio.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Ya existe una Unidad de Negocio con este nombre.')

        return nombre
        
# -- Proyecto
class ProyectoForm(forms.ModelForm):
    unidad_negocio_principal = forms.ModelChoiceField(
        queryset=UnidadNegocio.objects.select_related().order_by('nombre'),
        required=True,
        label='Unidad de Negocio (UN)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Proyecto
        fields = ['nombre', 'unidad_negocio_principal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Proyecto'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiqueta para el "vacío"
        self.fields['unidad_negocio_principal'].empty_label = 'Seleccione una UN'
        self.fields['unidad_negocio_principal'].label_from_instance = (
            lambda obj: f"{obj.codigo} · {obj.nombre}"
        )

    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        if not nombre:
            raise forms.ValidationError('Ingresa un nombre válido para el proyecto.')

        unidad = self.cleaned_data.get('unidad_negocio_principal')
        if not unidad and getattr(self.instance, 'unidad_negocio_principal_id', None):
            unidad = self.instance.unidad_negocio_principal
        if not unidad:
            raw_unidad = self.data.get(self.add_prefix('unidad_negocio_principal'))
            if raw_unidad:
                try:
                    unidad = UnidadNegocio.objects.get(pk=raw_unidad)
                except UnidadNegocio.DoesNotExist:
                    unidad = None

        if unidad:
            qs = Proyecto.objects.filter(
                nombre__iexact=nombre,
                unidad_negocio_principal=unidad
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    'Ya existe un proyecto con este nombre en la unidad seleccionada.'
                )

        return nombre