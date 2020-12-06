# standard library
import os

# Django
from django.core import management
from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata

# local Django
from config.settings.base import APPS_DIR
from django.db.models import Q
from apps.api.models import Person, MedicalTest, EMRProperty
from apps.training.models import Person as P
from apps.training.models import MedicalTest as M
from apps.training.models import EMRProperty as E


class Command(BaseCommand):
    help = 'Creates populates db with a few object for training'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Process started'))

        # P.objects.all().delete()
        # M.objects.all().delete()
        # E.objects.all().delete()

        persons = Person.objects.filter(
            Q(id__in=MedicalTest.objects.values_list('person_id').distinct('person_id')) & Q(
              id__in=EMRProperty.objects.values_list('person_id').distinct('person_id'))).distinct('id').order_by('id')

        p_ids = []
        ids_persons = {}
        for person in persons:
            if person.get_age() > 35:
                p = P.objects.create(
                    birthdate=person.birthdate,
                    sex=person.sex,
                    heart_disease_risk=True,
                    age=person.get_age(),
                    gender=person.get_gender()
                )
                p_ids.append(person.pk)
                ids_persons[person.pk] = p.pk
                if p.pk == 100:
                    break


        last_medical_tests = MedicalTest.objects.filter(person_id__in=p_ids).order_by(
            'person_id', 'property_id', '-end_date').distinct('person_id', 'property_id')

        m_for_training = []
        for m_test in last_medical_tests:
            M.objects.create(
                person_id=ids_persons[m_test.person_id],
                service_code=m_test.service_code,
                service_name=m_test.service_name,
                start_date=m_test.start_date,
                end_date=m_test.end_date,
                is_paraclinic=m_test.is_paraclinic,
                is_operation=m_test.is_operation,
                recommendations=m_test.recommendations,
                notes=m_test.notes,
                specialist_name=m_test.specialist_name,
                property_id=m_test.property_id,
                property_name=m_test.property_name,
                property_value=m_test.property_value,
                measurename=m_test.measurename
            )

        last_emr_properties = EMRProperty.objects.filter(person_id__in=p_ids).order_by(
            'person_id', 'property_id', '-end_date').distinct('person_id', 'property_id')

        e_for_training = []
        for e_prop in last_emr_properties:
            E.objects.create(
                person_id=ids_persons[e_prop.person_id],
                service_code=e_prop.service_code,
                service_name=e_prop.service_name,
                start_date=e_prop.start_date,
                end_date=e_prop.end_date,
                is_paraclinic=e_prop.is_paraclinic,
                is_operation=e_prop.is_operation,
                recommendations=e_prop.recommendations,
                notes=e_prop.notes,
                specialist_name=e_prop.specialist_name,
                property_id=e_prop.property_id,
                property_name=e_prop.property_name,
                property_value=e_prop.property_value,
                measurename=e_prop.measurename
            )

        # training_fixtures = os.listdir(os.path.join(APPS_DIR, 'training/fixtures/'))

        # management.call_command(loaddata.Command(), *training_fixtures, verbosity=0)
        self.stdout.write(self.style.SUCCESS('Successfully loading fixtures for training'))
