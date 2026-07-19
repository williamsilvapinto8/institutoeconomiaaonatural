from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import ImpactForm, ImpactResponse, ImpactAnswer, ImpactQuestion


@login_required
def respond_view(request, form_id):
    impact_form = get_object_or_404(ImpactForm, pk=form_id)
    try:
        benegnado = request.user.benegnado
    except Exception:
        messages.error(request, 'Perfil de participante não encontrado.')
        return redirect('dashboard')
        
    from events.models import Inscricao
    if not Inscricao.objects.filter(evento=impact_form.event, benegnado=benegnado, status='CONFIRMED').exists():
        messages.error(request, 'Você não está inscrito neste evento ou sua inscrição foi cancelada.')
        return redirect('dashboard')

    # Verificar se já respondeu
    if ImpactResponse.objects.filter(impact_form=impact_form, benegnado=benegnado).exists():
        messages.info(request, 'Você já respondeu este formulário.')
        return redirect('impact_forms:impact_success')

    questions = ImpactQuestion.objects.select_related('dimension').order_by('order')
    likert_questions = questions.filter(is_open=False)
    open_questions = questions.filter(is_open=True)

    if request.method == 'POST':
        errors = []
        # Validar todas as likert
        for q in likert_questions:
            val = request.POST.get(f'q_{q.id}')
            if not val or val not in ['1', '2', '3', '4', '5']:
                errors.append(f'Responda a pergunta {q.order}: {q.text[:50]}')

        if errors:
            messages.error(request, 'Por favor, responda todas as perguntas obrigatórias.')
            return render(request, 'impact_forms/respond.html', {
                'impact_form': impact_form,
                'likert_questions': likert_questions,
                'open_questions': open_questions,
                'post_data': request.POST,
            })

        with transaction.atomic():
            response = ImpactResponse.objects.create(
                impact_form=impact_form,
                benegnado=benegnado,
            )
            answers = []
            for q in likert_questions:
                val = int(request.POST.get(f'q_{q.id}'))
                answers.append(ImpactAnswer(
                    impact_response=response,
                    impact_question=q,
                    value=val,
                ))
            for q in open_questions:
                text = request.POST.get(f'q_{q.id}', '').strip()
                answers.append(ImpactAnswer(
                    impact_response=response,
                    impact_question=q,
                    text_answer=text,
                ))
            ImpactAnswer.objects.bulk_create(answers)

            messages.success(request, 'Respostas enviadas com sucesso! Obrigado pela sua contribuição.')
            return redirect('impact_forms:impact_success')

    return render(request, 'impact_forms/respond.html', {
        'impact_form': impact_form,
        'likert_questions': likert_questions,
        'open_questions': open_questions,
        'post_data': {},
    })


@login_required
def success_view(request):
    return render(request, 'impact_forms/success.html')
