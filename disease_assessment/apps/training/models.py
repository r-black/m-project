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
