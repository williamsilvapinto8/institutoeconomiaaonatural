from django.core.mail import send_mail
from django.conf import settings
from .models import EmailLog, EmailTracking
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def send_enrollment_confirmation(inscricao):
    evento = inscricao.evento
    benegnado = inscricao.benegnado
    user = benegnado.user
    email = user.email
    
    subject = f"Confirmação de Inscrição: {evento.title}"
    body = f"""Olá, {user.first_name}!
    
Sua inscrição no evento '{evento.title}' foi confirmada.

Detalhes do evento:
Data: {evento.date.strftime('%d/%m/%Y')} às {evento.start_time.strftime('%H:%M')}
Local/Plataforma: {evento.location if not evento.is_online else evento.online_platform}

Acesse seu painel para mais informações.
"""

    log = EmailLog.objects.create(
        recipient_email=email,
        recipient_user=user,
        subject=subject,
        body=body,
        event=evento,
        type='ENROLLMENT_CONFIRMATION'
    )
    
    # Criar registro de rastreamento
    tracking = EmailTracking.objects.create(email_log=log)
    
    # Montar as URLs absolutas usando a configuração do Django
    base_url = settings.BASE_URL
    pixel_url = base_url + reverse('communications:track_pixel', args=[tracking.token])
    
    # URL real do painel e a URL de rastreamento de clique apontando pra ela
    panel_url = base_url + reverse('dashboard')
    click_url = base_url + reverse('communications:track_click', args=[tracking.token]) + f"?next={panel_url}"

    # Versão HTML do e-mail com o pixel e o link rastreável
    html_message = f"""
    <html>
        <body>
            <p>Olá, {user.first_name}!</p>
            <p>Sua inscrição no evento <strong>{evento.title}</strong> foi confirmada.</p>
            <p>Detalhes do evento:<br>
            Data: {evento.date.strftime('%d/%m/%Y')} às {evento.start_time.strftime('%H:%M')}<br>
            Local/Plataforma: {evento.location if not evento.is_online else evento.online_platform}</p>
            <p><a href="{click_url}">Clique aqui para acessar seu painel</a></p>
            <img src="{pixel_url}" width="1" height="1" style="display:none;" />
        </body>
    </html>
    """

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message
        )
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail de confirmacao para {email}: {e}", exc_info=True)

def send_individual_reminder_task(inscricao_id, subject_template, body_template):
    from events.models import Inscricao
    
    try:
        inscricao = Inscricao.objects.get(pk=inscricao_id)
    except Inscricao.DoesNotExist:
        return
        
    evento = inscricao.evento
    benegnado = inscricao.benegnado
    user = benegnado.user
    email = user.email
    
    subject = subject_template.replace('{nome}', user.first_name).replace('{evento}', evento.title)
    body = body_template.replace('{nome}', user.first_name).replace('{evento}', evento.title)
    
    log = EmailLog.objects.create(
        recipient_email=email,
        recipient_user=user,
        subject=subject,
        body=body,
        event=evento,
        type='REMINDER'
    )
    
    tracking = EmailTracking.objects.create(email_log=log)
    
    base_url = settings.BASE_URL
    pixel_url = base_url + reverse('communications:track_pixel', args=[tracking.token])
    
    # URL do formulário de impacto: /impact/respond/<form_id>/
    # Assumindo que evento tenha pelo menos um form
    form = evento.impact_forms.first()
    if form:
        form_url = base_url + reverse('impact_forms:impact_respond', args=[form.id])
    else:
        form_url = base_url + reverse('dashboard')
        
    click_url = base_url + reverse('communications:track_click', args=[tracking.token]) + f"?next={form_url}"
    
    html_message = f"""
    <html>
        <body>
            <p>{body.replace(chr(10), '<br>').replace('{link}', f'<a href="{click_url}" style="display:inline-block; padding:10px 20px; background-color:#F3913A; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">Acessar Formulário</a>')}</p>
            <img src="{pixel_url}" width="1" height="1" style="display:none;" />
        </body>
    </html>
    """
    
    # Adicionar o link na versão de texto puro também
    body = body.replace('{link}', click_url)
    
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message
        )
        import time
        time.sleep(2) # Delay de 2 segundos para evitar rate limit do provedor (Napoleon)
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail de lembrete para {email}: {e}", exc_info=True)

def queue_mass_reminder_emails(inscricao_ids, subject_template, body_template):
    from django_q.tasks import async_task
    
    for inscricao_id in inscricao_ids:
        async_task('communications.utils.send_individual_reminder_task', inscricao_id, subject_template, body_template)
