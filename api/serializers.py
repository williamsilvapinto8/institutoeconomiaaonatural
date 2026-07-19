from rest_framework import serializers
from accounts.models import Benegnado
from people.models import Benegnador
from events.models import EventType, Evento, Inscricao
from impact_forms.models import ImpactForm, ImpactResponse, ImpactAnswer, ImpactDimension, ImpactQuestion


class InscricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscricao
        fields = ['id', 'evento', 'benegnado', 'status', 'origin', 'created_at']

class BenegnadoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Benegnado
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'company', 'role', 'city']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class BenegnadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benegnador
        fields = ['id', 'name', 'email', 'phone', 'bio', 'linkedin_url', 'instagram_url']


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ['id', 'name']


class EventoSerializer(serializers.ModelSerializer):
    event_type = EventTypeSerializer(read_only=True)
    total_participants = serializers.IntegerField(read_only=True)
    response_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'title', 'description', 'event_type', 'date',
            'start_time', 'end_time', 'location', 'is_online',
            'online_platform', 'online_link', 'total_participants', 'response_rate'
        ]


class ImpactDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactDimension
        fields = ['id', 'code', 'name', 'weight']


class ImpactFormSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = ImpactForm
        fields = ['id', 'name', 'event', 'event_title']


class ImpactResponseSerializer(serializers.ModelSerializer):
    iih_score = serializers.SerializerMethodField()

    class Meta:
        model = ImpactResponse
        fields = ['id', 'impact_form', 'benegnado', 'created_at', 'iih_score']

    def get_iih_score(self, obj):
        return obj.calculate_iih()
