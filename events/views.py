from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Evento, Inscricao, EventType
from communications.utils import send_enrollment_confirmation


@login_required
def dashboard_view(request):
    try:
        benegnado = request.user.benegnado
        inscricoes = Inscricao.objects.filter(benegnado=benegnado).select_related('evento')
        
        user_eventos = []
        for inscricao in inscricoes:
            evento = inscricao.evento
            responded = False
            # Check if user responded to this event's form
            if inscricao.status == 'CONFIRMED':
                responded = any(
                    form.responses.filter(benegnado=benegnado).exists()
                    for form in evento.impact_forms.all()
                )
            user_eventos.append({
                'evento': evento,
                'inscricao': inscricao,
                'responded': responded
            })
    except Exception:
        user_eventos = []
        benegnado = None
    
    is_benegnador = hasattr(request.user, 'benegnador')
    
    context = {
        'user_eventos': user_eventos,
        'has_benegnado': benegnado is not None,
        'is_benegnador': is_benegnador,
    }
    
    return render(request, 'events/dashboard.html', context)


def public_event_list(request):
    eventos = Evento.objects.filter(is_public_enrollment_open=True, date__gte=timezone.now().date()).order_by('date')
    return render(request, 'events/public_list.html', {'eventos': eventos})


def public_event_detail(request, public_slug):
    evento = get_object_or_404(Evento, public_slug=public_slug)
    is_enrolled = False
    is_cancelled = False
    
    if request.user.is_authenticated and hasattr(request.user, 'benegnado'):
        inscricao = Inscricao.objects.filter(evento=evento, benegnado=request.user.benegnado).first()
        if inscricao:
            is_enrolled = inscricao.status == 'CONFIRMED'
            is_cancelled = inscricao.status == 'CANCELLED'
            
    context = {
        'evento': evento,
        'is_enrolled': is_enrolled,
        'is_cancelled': is_cancelled,
    }
    return render(request, 'events/public_detail.html', context)


@login_required
def enroll_view(request, event_id):
    if request.method == 'POST':
        evento = get_object_or_404(Evento, pk=event_id)
        try:
            benegnado = request.user.benegnado
        except Exception:
            messages.error(request, 'Apenas participantes (Benegnados) podem se inscrever.')
            return redirect('public_event_detail', public_slug=evento.public_slug)
            
        if not evento.is_public_enrollment_open:
            messages.error(request, 'As inscrições para este evento estão fechadas.')
            return redirect('public_event_detail', public_slug=evento.public_slug)
            
        if evento.vacancies_left is not None and evento.vacancies_left <= 0:
            messages.error(request, 'Não há mais vagas disponíveis para este evento.')
            return redirect('public_event_detail', public_slug=evento.public_slug)
            
        inscricao, created = Inscricao.objects.get_or_create(
            evento=evento,
            benegnado=benegnado,
            defaults={'origin': 'SELF_ENROLLED', 'status': 'CONFIRMED'}
        )
        
        if not created:
            if inscricao.status == 'CANCELLED':
                inscricao.status = 'CONFIRMED'
                inscricao.save()
                messages.success(request, 'Inscrição reativada com sucesso! Você receberá um e-mail de confirmação.')
                send_enrollment_confirmation(inscricao)
            else:
                messages.info(request, 'Você já está inscrito neste evento.')
        else:
            messages.success(request, 'Inscrição realizada com sucesso! Você receberá um e-mail de confirmação.')
            send_enrollment_confirmation(inscricao)
            
        return redirect('public_event_detail', public_slug=evento.public_slug)
    return redirect('public_event_list')


@login_required
def unenroll_view(request, event_id):
    if request.method == 'POST':
        evento = get_object_or_404(Evento, pk=event_id)
        try:
            benegnado = request.user.benegnado
            inscricao = Inscricao.objects.get(evento=evento, benegnado=benegnado)
            inscricao.status = 'CANCELLED'
            inscricao.save()
            messages.success(request, 'Inscrição cancelada com sucesso.')
        except Exception:
            messages.error(request, 'Inscrição não encontrada.')
    return redirect('dashboard')


@login_required
def create_evento_view(request):
    is_staff = request.user.is_staff
    is_benegnador = hasattr(request.user, 'benegnador')
    
    if not (is_staff or is_benegnador):
        messages.error(request, 'Você não tem permissão para criar eventos.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        event_type_id = request.POST.get('event_type')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location', '')
        is_online = request.POST.get('is_online') == 'on'
        online_platform = request.POST.get('online_platform', '')
        online_link = request.POST.get('online_link', '')
        max_participants = request.POST.get('max_participants')
        
        try:
            event_type = EventType.objects.get(pk=event_type_id)
            evento = Evento.objects.create(
                title=title,
                description=description,
                event_type=event_type,
                date=date,
                start_time=start_time,
                end_time=end_time,
                location=location,
                is_online=is_online,
                online_platform=online_platform,
                online_link=online_link,
                max_participants=int(max_participants) if max_participants else None,
                created_by=request.user
            )
            if is_benegnador:
                evento.benegnadores.add(request.user.benegnador)
                
            messages.success(request, 'Evento criado com sucesso e publicado publicamente!')
            return redirect('public_event_detail', public_slug=evento.public_slug)
        except Exception as e:
            messages.error(request, f'Erro ao criar evento: {str(e)}')
            
    event_types = EventType.objects.all()
    return render(request, 'events/create_evento.html', {'event_types': event_types})

@login_required
def event_responses_dashboard(request, event_id):
    from communications.utils import queue_mass_reminder_emails
    
    if not request.user.is_staff:
        messages.error(request, 'Acesso restrito à equipe staff.')
        return redirect('dashboard')
        
    evento = get_object_or_404(Evento, pk=event_id)
    
    # Inscrições confirmadas
    inscricoes = Inscricao.objects.filter(evento=evento, status='CONFIRMED').select_related('benegnado__user')
    
    # Formulários do evento
    forms = evento.impact_forms.all()
    
    responded = []
    pending = []
    
    for inscricao in inscricoes:
        # Check se o benegnado respondeu a qualquer form do evento
        has_responded = False
        for form in forms:
            if form.responses.filter(benegnado=inscricao.benegnado).exists():
                has_responded = True
                break
                
        if has_responded:
            responded.append(inscricao)
        else:
            pending.append(inscricao)
            
    if request.method == 'POST':
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        
        if not subject or not body:
            messages.error(request, 'Assunto e mensagem são obrigatórios.')
        else:
            # Lista de IDs das inscrições pendentes para enviar para a fila
            pending_ids = [insc.id for insc in pending]
            if pending_ids:
                queue_mass_reminder_emails(pending_ids, subject, body)
                messages.success(request, f'{len(pending_ids)} e-mails de lembrete adicionados à fila de envio!')
            else:
                messages.warning(request, 'Não há usuários pendentes para enviar lembrete.')
            return redirect('admin_event_responses', event_id=evento.id)
            
    context = {
        'evento': evento,
        'responded': responded,
        'pending': pending,
    }
    
    return render(request, 'events/admin_responses_dashboard.html', context)
