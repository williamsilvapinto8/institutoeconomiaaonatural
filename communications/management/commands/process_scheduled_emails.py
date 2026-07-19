"""
Management command: process_scheduled_emails

Envia lembretes automaticos para participantes que ainda nao
responderam o formulario de impacto do evento.

Uso: python manage.py process_scheduled_emails
Cron sugerido: */15 * * * * python manage.py process_scheduled_emails
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from events.models import Evento
from impact_forms.models import ImpactForm, ImpactResponse
from communications.models import EmailLog, EmailTracking


class Command(BaseCommand):
    help = 'Envia lembretes de formulario para participantes que ainda nao responderam'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula o envio sem realmente enviar e-mails',
        )
        parser.add_argument(
            '--days-after',
            type=int,
            default=3,
            help='Numero de dias apos o evento para enviar o lembrete (padrao: 3)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_after = options['days_after']
        hoje = timezone.now().date()
        sent = 0
        skipped = 0

        eventos = Evento.objects.filter(date__lte=hoje).prefetch_related(
            'impact_forms'
        )

        for evento in eventos:
            forms = evento.impact_forms.all()
            if not forms.exists():
                continue

            for form in forms:
                confirmed_benegnados = [insc.benegnado for insc in evento.inscricoes.filter(status='CONFIRMED')]
                for benegnado in confirmed_benegnados:
                    # Verificar se ja respondeu
                    already_responded = ImpactResponse.objects.filter(
                        impact_form=form,
                        benegnado=benegnado
                    ).exists()

                    if already_responded:
                        skipped += 1
                        continue

                    # Verificar se ja foi enviado lembrete recente (ultimas 24h)
                    recent_reminder = EmailLog.objects.filter(
                        recipient_user=benegnado.user,
                        event=evento,
                        type='REMINDER',
                        sent_at__gte=timezone.now() - timezone.timedelta(hours=24)
                    ).exists()

                    if recent_reminder:
                        skipped += 1
                        continue

                    # Montar e enviar o e-mail
                    subject = f'Lembrete: Avalie o evento "{evento.title}"'
                    body = (
                        f'Ola, {benegnado.user.first_name or benegnado.user.username}!\n\n'
                        f'Voce ainda nao preencheu o formulario de avaliacao do evento '
                        f'"{evento.title}" ({evento.date}).\n\n'
                        f'Sua opiniao e muito importante para nos!\n\n'
                        f'Acesse: http://localhost:8000/impact/respond/{form.id}/\n\n'
                        f'Obrigado,\nEquipe Instituto Economia ao Natural'
                    )

                    if not dry_run:
                        try:
                            send_mail(
                                subject=subject,
                                message=body,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[benegnado.user.email],
                                fail_silently=False,
                            )
                            log = EmailLog.objects.create(
                                recipient_email=benegnado.user.email,
                                recipient_user=benegnado.user,
                                subject=subject,
                                body=body,
                                event=evento,
                                type='REMINDER',
                            )
                            EmailTracking.objects.create(email_log=log)
                            sent += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  Lembrete enviado para: {benegnado.user.email}'
                                )
                            )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  Erro ao enviar para {benegnado.user.email}: {e}')
                            )
                    else:
                        sent += 1
                        self.stdout.write(f'  [DRY-RUN] Enviaria para: {benegnado.user.email}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nConcluido: {sent} lembretes enviados, {skipped} ignorados.'
            )
        )
