from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from people.models import Benegnador
from accounts.models import Benegnado


class EventType(models.Model):
    name = models.CharField('Tipo', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Evento'

    def __str__(self):
        return self.name


class Evento(models.Model):
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descrição', blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT, verbose_name='Tipo')
    date = models.DateField('Data')
    start_time = models.TimeField('Início')
    end_time = models.TimeField('Término')
    location = models.CharField('Local', max_length=255, blank=True)
    is_online = models.BooleanField('Online?', default=False)
    online_platform = models.CharField('Plataforma Online', max_length=100, blank=True)
    online_link = models.URLField('Link Online', blank=True)
    benegnadores = models.ManyToManyField(Benegnador, blank=True, verbose_name='Benegnadores')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Criado por')
    is_public_enrollment_open = models.BooleanField('Inscrição Pública Aberta?', default=True)
    max_participants = models.PositiveIntegerField('Vagas Máximas', null=True, blank=True)
    public_slug = models.SlugField('Slug Público', unique=True, blank=True, max_length=255)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-date']

    def __str__(self):
        return f'{self.title} ({self.date})'

    def save(self, *args, **kwargs):
        if not self.public_slug:
            base_slug = slugify(f"{self.title}-{self.date}")
            slug = base_slug
            counter = 1
            while Evento.objects.filter(public_slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.public_slug = slug
        super().save(*args, **kwargs)

    @property
    def total_participants(self):
        return self.inscricoes.filter(status='CONFIRMED').count()
        
    @property
    def vacancies_left(self):
        if self.max_participants is None:
            return None
        left = self.max_participants - self.total_participants
        return max(0, left)

    @property
    def response_rate(self):
        total = self.total_participants
        if total == 0:
            return 0
        from impact_forms.models import ImpactResponse, ImpactForm
        forms = ImpactForm.objects.filter(event=self)
        if not forms.exists():
            return 0
        confirmed_benegnados = self.inscricoes.filter(status='CONFIRMED').values_list('benegnado', flat=True)
        responded = ImpactResponse.objects.filter(
            impact_form__in=forms,
            benegnado__in=confirmed_benegnados
        ).values('benegnado').distinct().count()
        return round((responded / total) * 100, 1)


class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
    ]
    ORIGIN_CHOICES = [
        ('SELF_ENROLLED', 'Auto-Inscrito'),
        ('ADMIN_ADDED', 'Adicionado pelo Admin'),
    ]
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes', verbose_name='Evento')
    benegnado = models.ForeignKey(Benegnado, on_delete=models.CASCADE, related_name='inscricoes', verbose_name='Participante')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    origin = models.CharField('Origem', max_length=20, choices=ORIGIN_CHOICES, default='SELF_ENROLLED')
    created_at = models.DateTimeField('Data de Inscrição', auto_now_add=True)

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        unique_together = ('evento', 'benegnado')

    def __str__(self):
        return f'{self.benegnado} em {self.evento}'
