from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import SignupForm
from .models import Benegnado


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = User.objects.create_user(
                username=d['username'],
                email=d['email'],
                password=d['password1'],
                first_name=d['first_name'],
                last_name=d['last_name'],
            )
            Benegnado.objects.create(
                user=user,
                phone=d.get('phone', ''),
                company=d.get('company', ''),
                role=d.get('role', ''),
                city=d.get('city', ''),
            )
            login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.first_name}! Sua conta foi criada com sucesso.')
            next_url = request.GET.get('next') or request.POST.get('next', '/dashboard/')
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form, 'next': request.GET.get('next', '')})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
