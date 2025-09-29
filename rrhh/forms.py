from django import forms
from django.forms import formset_factory

from ventas.models import Proyecto

from .models import Personal


class DateInput(forms.DateInput):
    input_type = "date"


class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        exclude = ["codigo"]
        widgets = {
            "nombres": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombres"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellidos"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cargo"}),
            "dni": forms.TextInput(attrs={"class": "form-control", "placeholder": "Documento de identidad", "maxlength": "8"}),
            "empresa_afp": forms.TextInput(attrs={"class": "form-control", "placeholder": "Empresa AFP"}),
            "numero_afp": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número AFP"}),
            "fecha_ingreso": DateInput(attrs={"class": "form-control"}),
            "tipo_comision_afp": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tipo de comisión"}),
            "bono": forms.TextInput(attrs={"class": "form-control", "placeholder": "Bono"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "modalidad": forms.TextInput(attrs={"class": "form-control", "placeholder": "Modalidad"}),
            "domicilio": forms.TextInput(attrs={"class": "form-control", "placeholder": "Domicilio"}),
            "inicio_de_contrato": DateInput(attrs={"class": "form-control"}),
            "vencimiento_contrato": DateInput(attrs={"class": "form-control"}),
            "contacto_emergencia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contacto de emergencia"}),
            "num_emergencia": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de emergencia", "maxlength": "9"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
            "profesion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Profesión"}),
            "id_proyecto": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proyectos = Proyecto.objects.all().order_by("nombre")
        self.fields["id_proyecto"].queryset = proyectos
        self.fields["id_proyecto"].label = "Proyecto asignado"
        self.fields["id_proyecto"].label_from_instance = lambda obj: f"{obj.nombre} ({obj.codigo})"


class HijoForm(forms.Form):
    nombre_hijo = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"})
    )
    cumpleaños_hijo = forms.DateField(
        required=False,
        widget=DateInput(attrs={"class": "form-control"})
    )


HijoFormSet = formset_factory(HijoForm, extra=5, max_num=5, validate_max=True)
