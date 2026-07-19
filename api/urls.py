from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BenegnadoViewSet, BenegnadorViewSet, EventoViewSet,
    ImpactFormViewSet, ImpactResponseViewSet, InscricaoViewSet
)

router = DefaultRouter()
router.register(r'benegnados', BenegnadoViewSet)
router.register(r'benegnadores', BenegnadorViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'impact-forms', ImpactFormViewSet)
router.register(r'impact-responses', ImpactResponseViewSet)
router.register(r'inscricoes', InscricaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
