from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
# Create your views here.
def sign_in(request):
    if request.method == 'GET':
        return render(request, 'login.html',{
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'login.html',{
                'form': AuthenticationForm(),
                'error': 'Usuario o contraseña inválidos'
            })
        
        else:
            login(request, user)
            return render(request, 'home.html')

@login_required
def home(request):
    return render(request, 'home.html')