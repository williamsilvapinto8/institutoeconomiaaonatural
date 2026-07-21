from django.shortcuts import redirect
from django.urls import reverse

class MustChangePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Verifica se o usuário tem o perfil Benegnado e se precisa trocar a senha
            try:
                benegnado = request.user.benegnado
                if benegnado.must_change_password:
                    # Permite acesso apenas às URLs de mudança de senha e logout
                    allowed_urls = [
                        reverse('accounts:change_password'),
                        reverse('accounts:logout'),
                    ]
                    if request.path not in allowed_urls and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                        return redirect('accounts:change_password')
            except AttributeError:
                # O usuário logado não tem o perfil de Benegnado (ex: Superuser ou Benegnador)
                pass

        response = self.get_response(request)
        return response
