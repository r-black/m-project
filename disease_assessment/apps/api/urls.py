"""
api URL Configuration
"""
from django.urls import include, path
from rest_framework import routers

from apps.api.views import (
    PersonViewSet,
    MedicalRecordViewSet,
    DispensaryRegistrationViewSet,
    AnamnesisViewSet,
    MedicalTestViewSet,
    EMRPropertyViewSet
)

router = routers.DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'medical-records', MedicalRecordViewSet)
router.register(r'dispensary-registrations', DispensaryRegistrationViewSet)
router.register(r'anamnesis', AnamnesisViewSet)
router.register(r'medical-tests', MedicalTestViewSet)
router.register(r'emr-properties', EMRPropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
