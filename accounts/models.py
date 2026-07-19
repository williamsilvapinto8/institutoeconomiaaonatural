from django.db import models
from django.contrib.auth.models import User


class Benegnado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='benegnado')
    phone = models.CharField('Telefone/WhatsApp', max_length=20, blank=True)
    company = models.CharField('Empresa', max_length=150, blank=True)
    role = models.CharField('Cargo', max_length=100, blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Benegnado'
        verbose_name_plural = 'Benegnados'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'
