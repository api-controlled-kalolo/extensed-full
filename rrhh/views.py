from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import HijoFormSet, PersonalForm
from .models import HijosPersonal, Personal


def dashboard(request):
	context = {
		"personal_count": Personal.objects.count(),
	}
	return render(request, "rrhh/dashboard.html", context)


def personal_list(request):
	personal_queryset = Personal.objects.select_related("id_proyecto").order_by("apellidos", "nombres")
	context = {
		"personal_list": personal_queryset,
	}
	return render(request, "rrhh/personal_list.html", context)


def personal_create(request):
	selected_children = 0

	if request.method == "POST":
		personal_form = PersonalForm(request.POST)
		hijo_formset = HijoFormSet(request.POST, prefix="hijo")
		try:
			selected_children = int(request.POST.get("children_count", 0))
		except (TypeError, ValueError):
			selected_children = 0

		selected_children = max(0, min(selected_children, len(hijo_formset.forms)))

		if personal_form.is_valid() and hijo_formset.is_valid():
			valid_children = []
			has_child_errors = False

			for index, child_form in enumerate(hijo_formset.forms):
				if index >= selected_children:
					break

				nombre = child_form.cleaned_data.get("nombre_hijo")
				cumple = child_form.cleaned_data.get("cumpleaños_hijo")

				if not nombre or not cumple:
					child_form.add_error(None, "Completa el nombre y la fecha de nacimiento")
					has_child_errors = True
				else:
					valid_children.append((nombre, cumple))

			if has_child_errors:
				messages.error(request, "Revisa los datos de los hijos seleccionados.")
			else:
				with transaction.atomic():
					personal = personal_form.save()
					for nombre, cumple in valid_children:
						HijosPersonal.objects.create(
							id_personal=personal,
							nombre_hijo=nombre,
							cumpleaños_hijo=cumple
						)

				messages.success(request, "Personal registrado correctamente.")
				return redirect("rrhh:personal_create")
	else:
		personal_form = PersonalForm()
		hijo_formset = HijoFormSet(prefix="hijo")

	context = {
		"personal_form": personal_form,
		"hijo_formset": hijo_formset,
		"children_options": range(0, len(hijo_formset.forms) + 1),
		"selected_children": selected_children,
	}

	return render(request, "rrhh/personal_form.html", context)
