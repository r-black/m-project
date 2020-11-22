from rest_framework import viewsets, pagination, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import pandas as pd

from apps.api.models import (
    Person,
    MedicalRecord,
    DispensaryRegistration,
    Anamnesis
)
from apps.api.serializers import (
    PersonSerializer,
    MedicalRecordSerializer,
    DispensaryRegistrationSerializer,
    AnamnesisSerializer
)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['get'], permission_classes=(permissions.IsAuthenticated,))
    def persons_with_medical_records(self, request, *args, **kwargs):
        """
        All information about persons with medical records.
        """
        queryset = self.filter_queryset(
            self.get_queryset().filter(id__in=MedicalRecord.objects.values_list('person_id').distinct()))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        return Response(data)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        """
        Create a medical record with heart disease risk prediction.
        """
        person_id = self.request.data.get('person_id')
        birthdate = self.request.data.get('person').birthdate
        sex = self.request.data.get('person').sex
        blood_pressure = self.request.data.get('blood_pressure')
        heart_rate = self.request.data.get('heart_rate')

        # Unpickle model
        model = pd.read_pickle(r"new_model.pickle")
        # Make prediction
        result = model.predict([[person_id, birthdate, sex, blood_pressure, heart_rate]])

        heart_disease_risk = result[0]
        Person.objects.filter(id=person_id).update(heart_disease_risk=heart_disease_risk)
        serializer.save()


class DispensaryRegistrationViewSet(viewsets.ModelViewSet):
    queryset = DispensaryRegistration.objects.all()
    serializer_class = DispensaryRegistrationSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)


class AnamnesisViewSet(viewsets.ModelViewSet):
    queryset = Anamnesis.objects.all()
    serializer_class = AnamnesisSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)
