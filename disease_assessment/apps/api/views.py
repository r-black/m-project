from rest_framework import viewsets, pagination, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

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
    def all_info(self, request, *args, **kwargs):
        """
        All information about persons.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data # pagination data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        return Response(data)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)


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
