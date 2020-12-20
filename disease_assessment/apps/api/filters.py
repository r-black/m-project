from django_filters import rest_framework as filters

from apps.api.models import Person


class PersonFilter(filters.FilterSet):
    class Meta:
        model = Person
        fields = ('id', 'heart_disease_risk', 'birthdate', 'medical_tests__property_value',
            'emr_properties__property_value')
