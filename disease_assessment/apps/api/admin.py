from django.contrib import admin

from apps.api.models import (
    Person,
    MedicalRecord,
    DispensaryRegistration,
    Anamnesis
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
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
        'diagnosis',
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
