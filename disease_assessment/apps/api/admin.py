from django.contrib import admin

from apps.api.models import (
    Person,
    MedicalRecord,
    DispensaryRegistration,
    Anamnesis,
    MedicalTest,
    EMRProperty
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = (
        'id',
        'birthdate',
        'sex',
    )


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    list_display = (
        'person',
        'row_number',
        'clinical_course',
        'systolic_blood_pressure',
        'heart_rate',
        'blood_pressure',
        'blood_sugar',
        'cholesterol',
        'body_mass_index',
    )


@admin.register(DispensaryRegistration)
class DispensaryRegistrationAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    list_display = (
        'person',
        'disp_health_group_value',
        'diagnosis_note',
    )


@admin.register(Anamnesis)
class AnamnesisAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    list_display = (
        'person',
        'anamnesis_type_name',
        'anamnesis',
        'anamnesis_date',
    )


@admin.register(MedicalTest)
class MedicalTestAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    ordering = ('person_id',)
    list_display = (
        'person_id',
        'service_code',
        'service_name',
        'start_date',
        'end_date',
        'recommendations',
        'notes',
        'specialist_name',
        'property_id',
        'property_name',
        'property_value',
        'measurename'
    )


@admin.register(EMRProperty)
class EMRPropertyAdmin(admin.ModelAdmin):
    raw_id_fields = ('person',)
    ordering = ('person_id',)
    list_display = (
        'person_id',
        'service_code',
        'service_name',
        'start_date',
        'end_date',
        'recommendations',
        'notes',
        'specialist_name',
        'property_id',
        'property_name',
        'property_value',
        'measurename'
    )
