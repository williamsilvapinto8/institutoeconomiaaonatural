import io
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import EmailTracking


def pixel_view(request, token):
    """Retorna um pixel 1x1 transparente e registra a abertura."""
    tracking = get_object_or_404(EmailTracking, token=token)
    if not tracking.opened_at:
        tracking.opened_at = timezone.now()
        tracking.save(update_fields=['opened_at'])

    # Pixel PNG 1x1 transparente (bytes mínimos)
    pixel = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return HttpResponse(pixel, content_type='image/png')


def click_view(request, token):
    """Registra o clique e redireciona para a URL destino."""
    tracking = get_object_or_404(EmailTracking, token=token)
    if not tracking.clicked_at:
        tracking.clicked_at = timezone.now()
        tracking.save(update_fields=['clicked_at'])
    next_url = request.GET.get('next', '/')
    return HttpResponseRedirect(next_url)
