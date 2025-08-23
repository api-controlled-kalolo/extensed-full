from django import forms
from django.forms import inlineformset_factory
from .models import ActaServicioTecnico,Equipos_ActaServicioTecnico, Acciones_ActaServicioTecnico

class ActaServicioForm(forms.ModelForm):
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