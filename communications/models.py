import uuid
from django.db import models
from django.contrib.auth.models import User


class EmailLog(models.Model):
    TYPE_CHOICES = [
        ('INVITATION', 'Convite'),
        ('REMINDER', 'Lembrete'),
        ('POST_EVENT', 'Pós-Evento'),
        ('ENROLLMENT_CONFIRMATION', 'Confirmação de Inscrição'),
    ]
    recipient_email = models.EmailField('E-mail do Destinatário')
    recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuário')
    subject = models.CharField('Assunto', max_length=255)
    body = models.TextField('Corpo do E-mail')
    sent_at = models.DateTimeField('Enviado em', auto_now_add=True)
    event = models.ForeignKey('events.Evento', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Evento')
    type = models.CharField('Tipo', max_length=30, choices=TYPE_CHOICES, default='INVITATION')

    class Meta:
        verbose_name = 'Log de E-mail'
        verbose_name_plural = 'Logs de E-mail'
        ordering = ['-sent_at']

    def __str__(self):
        return f'[{self.type}] {self.subject} → {self.recipient_email}'


class EmailTracking(models.Model):
    email_log = models.ForeignKey(EmailLog, on_delete=models.CASCADE, related_name='trackings')
    token = models.UUIDField('Token', unique=True, default=uuid.uuid4)
    opened_at = models.DateTimeField('Aberto em', null=True, blank=True)
    clicked_at = models.DateTimeField('Clicado em', null=True, blank=True)

    class Meta:
        verbose_name = 'Rastreamento de E-mail'
        verbose_name_plural = 'Rastreamentos de E-mail'

    def __str__(self):
        return f'Tracking {self.token}'
