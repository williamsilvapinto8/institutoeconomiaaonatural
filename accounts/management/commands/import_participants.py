import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Benegnado
from events.models import Evento, Inscricao
from django.db import transaction

class Command(BaseCommand):
    help = 'Importa participantes a partir de um arquivo CSV e opcionalmente os inscreve em um evento.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Caminho para o arquivo CSV')
        parser.add_argument('--event', type=int, help='ID do evento para inscrever os usuários importados')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        event_id = options.get('event')
        
        evento = None
        if event_id:
            try:
                evento = Evento.objects.get(pk=event_id)
            except Evento.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'Evento com ID {event_id} não encontrado.'))
                return

        created_count = 0
        enrolled_count = 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                delimiter = ';' if ';' in first_line else ','
                f.seek(0)
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Strip spaces from field names in case of weird formatting
                reader.fieldnames = [name.strip() for name in reader.fieldnames if name]
                
                with transaction.atomic():
                    for row in reader:
                        email = row.get('email', '').strip()
                        if not email:
                            continue
                            
                        first_name = row.get('nome', '').strip()
                        last_name = row.get('sobrenome', '').strip()
                        telefone = row.get('telefone', '').strip()
                        empresa = row.get('empresa', '').strip()
                        cargo = row.get('cargo', '').strip()
                        cidade = row.get('cidade', '').strip()
                        
                        # Criar ou pegar User
                        user, user_created = User.objects.get_or_create(
                            username=email,
                            defaults={
                                'email': email,
                                'first_name': first_name,
                                'last_name': last_name
                            }
                        )
                        if user_created:
                            user.set_password('Mudar123!')  # Senha padrão
                            user.save()
                            
                        # Criar ou pegar Benegnado
                        benegnado, b_created = Benegnado.objects.get_or_create(
                            user=user,
                            defaults={
                                'phone': telefone,
                                'company': empresa,
                                'role': cargo,
                                'city': cidade
                            }
                        )
                        
                        if user_created:
                            created_count += 1
                            
                        # Inscrever no evento
                        if evento:
                            inscricao, i_created = Inscricao.objects.get_or_create(
                                evento=evento,
                                benegnado=benegnado,
                                defaults={'origin': 'ADMIN_ADDED', 'status': 'CONFIRMED'}
                            )
                            if i_created or inscricao.status != 'CONFIRMED':
                                inscricao.status = 'CONFIRMED'
                                inscricao.save()
                                enrolled_count += 1
                                
            self.stdout.write(self.style.SUCCESS(f'Importação concluída! {created_count} novos usuários criados.'))
            if evento:
                self.stdout.write(self.style.SUCCESS(f'{enrolled_count} inscrições confirmadas no evento "{evento.title}".'))
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao importar arquivo: {e}'))
