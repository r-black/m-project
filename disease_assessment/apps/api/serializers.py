from rest_framework import serializers

from apps.api.models import (
    Person,
    MedicalRecord,
    DispensaryRegistration,
    Anamnesis
)


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = (
            'person_id',
            'row_number',
            'emergency',
            'prime',
            'transportation_type_name',
            'enter_diagnosis',
            'diagnoses_divergence',
            'in_date',
            'work_capacity_name',
            'clinical_course',
            'out_date',
            'diagnosis',
            'm_record_mkb_name',
            'visit_result_name',
        )


class DispensaryRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DispensaryRegistration
        fields = (
            'person_id',
            'disp_health_group_value',
            'd_registration_mkb_name',
            'diagnosis_note',
            'note',
            'input_date',
            'start_date',
            'end_date',
            'change_date',
            'disp_remove_reason_name',
        )


class AnamnesisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anamnesis
        fields = (
            'person_id',
            'anamnesis_type_name',
            'anamnesis_date',
            'anamnesis',
        )


class PersonSerializer(serializers.ModelSerializer):
    medical_records =serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = (
            'id',
            'birthdate',
            'sex',
            'medical_records'
        )

    def get_medical_records(self, person):
        medical_records = MedicalRecord.objects.filter(
            person=person
        )
        serializer = MedicalRecordSerializer(
            medical_records,
            many=True
        )
        return serializer.data
