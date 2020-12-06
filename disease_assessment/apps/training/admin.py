from django.contrib import admin

from apps.training.models import (
    Person,
    MedicalTest,
    EMRProperty
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'birthdate',
        'sex',
        'heart_disease_risk'
    )


@admin.register(MedicalTest)
class MedicalTestAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    list_filter = ('service_name',)
    list_display = (
        'person_id',
        'service_name',
        'start_date',
        'end_date',
        'recommendations',
        'notes',
        'specialist_name',
        'property_name',
        'property_value',
        'measurename'
    )


@admin.register(EMRProperty)
class EMRPropertyAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    list_filter = ('service_name',)
    list_display = (
        'person_id',
        'service_name',
        'start_date',
        'end_date',
        'recommendations',
        'notes',
        'specialist_name',
        'property_name',
        'property_value',
        'measurename'
    )
