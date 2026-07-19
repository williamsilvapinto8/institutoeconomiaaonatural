from rest_framework import viewsets, permissions
from accounts.models import Benegnado
from people.models import Benegnador
from events.models import Evento
from impact_forms.models import ImpactForm, ImpactResponse
from .serializers import (
    BenegnadoSerializer, BenegnadorSerializer, EventoSerializer,
    ImpactFormSerializer, ImpactResponseSerializer, InscricaoSerializer
)
from events.models import Evento, Inscricao


class BenegnadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Benegnado.objects.all().select_related('user')
    serializer_class = BenegnadoSerializer
    permission_classes = [permissions.IsAdminUser]


class BenegnadorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Benegnador.objects.all()
    serializer_class = BenegnadorSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Evento.objects.all().select_related('event_type')
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImpactFormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImpactForm.objects.all().select_related('event')
    serializer_class = ImpactFormSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImpactResponseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImpactResponse.objects.all().select_related('impact_form', 'benegnado')
    serializer_class = ImpactResponseSerializer
    permission_classes = [permissions.IsAdminUser]


class InscricaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Inscricao.objects.all().select_related('evento', 'benegnado')
    serializer_class = InscricaoSerializer
    permission_classes = [permissions.IsAdminUser]
