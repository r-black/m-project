import pandas as pd
from tqdm import tqdm
from datetime import datetime, date
from django.db import models
from django.conf import settings


def datetime_parse(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
    except Exception:
        pass


def date_parse(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value), '%d.%m.%Y').strftime('%Y-%m-%d')
    except Exception:
        pass


class Person(models.Model):
    birthdate = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=4, blank=True, null=True)
    heart_disease_risk = models.BooleanField(blank=True, null=True, default=False)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.age = self.get_age()
        self.gender = self.get_gender()
        super(Person, self).save(*args, **kwargs)

    def get_age(self):
        today = date.today()
        birthdate = self.birthdate
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    def get_gender(self):
        if self.sex == 'М':
            return 1
        else:
            return 0

    PERSONS_CSV_PATH = f'{settings.PROJECT_DIR}/data/raw/persons.csv'

    def __str__(self):
        return f'{self.id}'

    @classmethod
    def initialize(cls):
        cls.objects.all().delete()

        cls.objects.bulk_create([
            cls(
                id=row['PersonID'],
                birthdate=row['BirthDate'],
                sex=row['Sex'],
            )
            for index, row in tqdm(pd.read_csv(cls.PERSONS_CSV_PATH, sep=';').iterrows())
        ])
        print('Success')


class MedicalRecord(models.Model):
    person = models.ForeignKey(
        to='Person',
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    row_number = models.PositiveIntegerField(blank=True, null=True)
    emergency = models.PositiveIntegerField(blank=True, null=True)
    prime = models.PositiveIntegerField(blank=True, null=True)
    transportation_type_name = models.CharField(max_length=100, blank=True, null=True)
    enter_diagnosis = models.TextField(blank=True, null=True)
    diagnoses_divergence = models.TextField(blank=True, null=True)
    in_date = models.DateTimeField(blank=True, null=True)
    work_capacity_name = models.CharField(max_length=100, blank=True, null=True)
    clinical_course = models.TextField(blank=True, null=True)
    out_date = models.DateTimeField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    m_record_mkb_name = models.TextField(blank=True, null=True)
    visit_result_name = models.TextField(blank=True, null=True)
    heart_rate = models.PositiveIntegerField(blank=True, null=True)
    blood_pressure = models.CharField(max_length=100, blank=True, null=True)
    blood_sugar = models.CharField(max_length=100, blank=True, null=True)
    cholesterol = models.CharField(max_length=100, blank=True, null=True)
    body_mass_index = models.CharField(max_length=100, blank=True, null=True)
    systolic_blood_pressure = models.PositiveIntegerField(blank=True, null=True)
    diastolic_blood_pressure = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.systolic_blood_pressure = self.get_systolic_blood_pressure()
        self.diastolic_blood_pressure = self.get_diastolic_blood_pressure()

        person_id = self.person.id
        age = self.person.age
        gender = self.person.gender
        systolic_blood_pressure = self.systolic_blood_pressure
        diastolic_blood_pressure = self.diastolic_blood_pressure
        heart_rate = self.heart_rate

        # Unpickle model
        model = pd.read_pickle(r"new_model.pickle")
        # Make prediction
        result = model.predict(
            [[age, gender, systolic_blood_pressure, diastolic_blood_pressure, heart_rate]])

        heart_disease_risk = result[0]
        print(heart_disease_risk)
        Person.objects.filter(id=person_id).update(heart_disease_risk=heart_disease_risk)
        super(MedicalRecord, self).save(*args, **kwargs)

    def get_systolic_blood_pressure(self):
        if self.blood_pressure:
            return self.blood_pressure.split('/')[0]

    def get_diastolic_blood_pressure(self):
        if self.blood_pressure:
            return self.blood_pressure.split('/')[1]

    MEDICAL_RECORDS_CSV_PATH = f'{settings.PROJECT_DIR}/data/raw/medical_records.csv'

    def __str__(self):
        return f'{self.person}'

    @classmethod
    def initialize(cls):
        cls.objects.all().delete()

        cls.objects.bulk_create([
            cls(
                person_id=row['PersonID'],
                row_number=row['rn'],
                emergency=row['Emergency'],
                prime=row['Prime'],
                transportation_type_name=row['TransportationTypeName'],
                enter_diagnosis=row['EnterDiagnosis'],
                diagnoses_divergence=row['DiagnosesDivergence'],
                in_date=datetime_parse(row['InDate']),
                work_capacity_name=row['WorkCapacityName'],
                clinical_course=row['ClinicalCourse'],
                out_date=datetime_parse(row['OutDate']),
                diagnosis=row['Diagnosis'],
                m_record_mkb_name=row['MKBName'],
                visit_result_name=row['VisitResultName'],
            )
            for index, row in tqdm(pd.read_csv(cls.MEDICAL_RECORDS_CSV_PATH, sep=';').iterrows())
        ])
        print('Success')


class DispensaryRegistration(models.Model):
    person = models.ForeignKey(
        to='Person',
        on_delete=models.CASCADE,
        related_name='dispensary_registrations'
    )
    disp_health_group_value = models.CharField(max_length=100, blank=True, null=True)
    d_registration_mkb_name = models.TextField(blank=True, null=True)
    diagnosis_note = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    input_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    change_date = models.DateField(blank=True, null=True)
    disp_remove_reason_name = models.TextField(blank=True, null=True)

    DISPENSARY_REGISTRATION_CSV_PATH = f'{settings.PROJECT_DIR}/data/raw/dispensary_registration.csv'

    def __str__(self):
        return f'{self.person}'

    @classmethod
    def initialize(cls):
        cls.objects.all().delete()

        cls.objects.bulk_create([
            cls(
                person_id=row['PersonID_Ref'],
                disp_health_group_value=row['DispHealthGroupValue'],
                d_registration_mkb_name=row['MKBName'],
                diagnosis_note=row['DiagnosisNote'],
                note=row['Note'],
                input_date=date_parse(row['InputDate']),
                start_date=date_parse(row['StartDate']),
                end_date=date_parse(row['EndDate']),
                change_date=date_parse(row['ChangeDate']),
                disp_remove_reason_name=row['DispRemoveReasonName'],
            )
            for index, row in tqdm(pd.read_csv(cls.DISPENSARY_REGISTRATION_CSV_PATH, sep=';').iterrows())
        ])
        print('Success')


class Anamnesis(models.Model):
    person = models.ForeignKey(
        to='Person',
        on_delete=models.CASCADE,
        related_name='anamnesis'
    )
    anamnesis_type_name = models.CharField(max_length=100, blank=True, null=True)
    anamnesis_date = models.DateField(blank=True, null=True)
    anamnesis = models.TextField(blank=True, null=True)

    ANAMNESIS_CSV_PATH = f'{settings.PROJECT_DIR}/data/raw/anamnesis.csv'

    def __str__(self):
        return f'{self.person}'

    @classmethod
    def initialize(cls):
        cls.objects.all().delete()

        cls.objects.bulk_create([
            cls(
                person_id=row['PersonID_Ref'],
                anamnesis_type_name=row['AnamnesisTypeName'],
                anamnesis_date=row['AnamnesisDate'],
                anamnesis=row['Anamnesis'],
            )
            for index, row in tqdm(pd.read_csv(cls.ANAMNESIS_CSV_PATH, sep=';').iterrows())
        ])
        print('Success')


class MedicalTest(models.Model):
    person = models.ForeignKey(
        to='Person',
        on_delete=models.CASCADE,
        related_name='medical_tests'
    )
    service_code = models.CharField(max_length=100, blank=True, null=True)
    service_name = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_paraclinic = models.CharField(max_length=100, blank=True, null=True)
    is_operation = models.CharField(max_length=100, blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    specialist_name = models.CharField(max_length=255, blank=True, null=True)
    property_id = models.CharField(max_length=100, blank=True, null=True)
    property_name = models.CharField(max_length=255, blank=True, null=True)
    property_value = models.CharField(max_length=255, blank=True, null=True)
    measurename = models.CharField(max_length=100, blank=True, null=True)

    MEDICAL_TESTS_CSV_PATH = f'{settings.PROJECT_DIR}/data/raw/medical_tests.csv'

    def __str__(self):
        return f'{self.person}'

    @classmethod
    def initialize(cls):
        cls.objects.all().delete()

        cls.objects.bulk_create([
            cls(
                person_id=row['PersonID_Ref'],
                service_code=row['servicecode'],
                service_name=row['servicename'],
                start_date=row['StartDateTime'],
                end_date=row['EndDateTime'],
                is_paraclinic=row['IsParaclinic'],
                is_operation=row['IsOperation'],
                recommendations=row['Recommendations'],
                notes=row['Notes'],
                specialist_name=row['SpecialistName'],
                property_id=row['PropertyID'],
                property_name=row['PropertyNameSave'],
                property_value=row['ServiceRecordPropertyValue'],
                measurename=row['measurename']
            )
            for index, row in tqdm(pd.read_csv(
                cls.MEDICAL_TESTS_CSV_PATH, sep=';',
                dtype={12: object, 13: object, 17: object},
                low_memory=False).tail(700000).sort_values('PersonID_Ref').iterrows())
        ])
        print('Success')


class EMRProperty(models.Model):
    person = models.ForeignKey(
        to='Person',
        on_delete=models.CASCADE,
        related_name='emr_properties'
    )
    service_code = models.CharField(max_length=100, blank=True, null=True)
    service_name = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_paraclinic = models.CharField(max_length=100, blank=True, null=True)
    is_operation = models.CharField(max_length=100, blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    specialist_name = models.CharField(max_length=255, blank=True, null=True)
    property_id = models.CharField(max_length=100, blank=True, null=True)
    property_name = models.CharField(max_length=255, blank=True, null=True)
    property_value = models.CharField(max_length=255, blank=True, null=True)
    measurename = models.CharField(max_length=100, blank=True, null=True)

    EMR_PROPERTIES_CSV_PATH = f'{settings.PROJECT_DIR}/data/raw/EMR_properties.csv'

    def __str__(self):
        return f'{self.person}'

    @classmethod
    def initialize(cls):
        cls.objects.all().delete()

        cls.objects.bulk_create([
            cls(
                person_id=row['PersonID_Ref'],
                service_code=row['servicecode'],
                service_name=row['servicename'],
                start_date=row['StartDateTime'],
                end_date=row['EndDateTime'],
                is_paraclinic=row['IsParaclinic'],
                is_operation=row['IsOperation'],
                recommendations=row['Recommendations'],
                notes=row['Notes'],
                specialist_name=row['SpecialistName'],
                property_id=row['PropertyID'],
                property_name=row['PropertyNameSave'],
                property_value=row['ServiceRecordPropertyValue'],
                measurename=row['measurename']
            )
            for index, row in tqdm(pd.read_csv(
                cls.EMR_PROPERTIES_CSV_PATH, sep=';', nrows=600000,
                dtype={12: object, 13: object, 17: object}, low_memory=False).iterrows())
        ])
        print('Success')
