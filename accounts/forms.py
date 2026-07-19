from django import forms
from django.contrib.auth.models import User
from .models import Benegnado


class SignupForm(forms.Form):
    first_name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Sobrenome', max_length=100)
    email = forms.EmailField(label='E-mail')
    username = forms.CharField(label='Usuário', max_length=150)
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)
    phone = forms.CharField(label='Telefone/WhatsApp', max_length=20, required=False)
    company = forms.CharField(label='Empresa', max_length=150, required=False)
    role = forms.CharField(label='Cargo', max_length=100, required=False)
    city = forms.CharField(label='Cidade', max_length=100, required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned_data
