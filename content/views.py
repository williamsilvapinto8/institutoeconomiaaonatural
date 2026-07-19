from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import ContentItem


@login_required
def content_view(request, content_id):
    item = get_object_or_404(ContentItem, pk=content_id)
    try:
        benegnado = request.user.benegnado
    except Exception:
        raise Http404

    # Verifica se o benegnado está inscrito no evento do conteúdo
    from events.models import Inscricao
    if not Inscricao.objects.filter(evento=item.event, benegnado=benegnado, status='CONFIRMED').exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    return render(request, 'content/view.html', {'item': item})
