from django import forms
from django.forms import inlineformset_factory
from .models import ActaServicioTecnico,Equipos_ActaServicioTecnico, Acciones_ActaServicioTecnico

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