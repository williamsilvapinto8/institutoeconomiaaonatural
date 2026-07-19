from django.db import models


from django.contrib.auth.models import User

class Benegnador(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuário Vinculado')
    name = models.CharField('Nome', max_length=200)
    email = models.EmailField('E-mail', unique=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    bio = models.TextField('Bio', blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)

    class Meta:
        verbose_name = 'Benegnador'
        verbose_name_plural = 'Benegnadores'
        ordering = ['name']

    def __str__(self):
        return self.name
