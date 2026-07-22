from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def is_staff_or_benegnador(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or hasattr(user, 'benegnador')


def staff_or_benegnador_required(view_func):
    def check_perms(user):
        return is_staff_or_benegnador(user)
        
    actual_decorator = user_passes_test(
        check_perms,
        login_url='accounts:login',
        redirect_field_name=None
    )
    return actual_decorator(view_func)


class StaffOrBenegnadorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_staff_or_benegnador(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Apenas membros da equipe (Staff) ou Benegnadores possuem permissão para gerenciar artigos.")
        return redirect('blog:post_list')
