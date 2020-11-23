# standard library
import os

# Django
from django.contrib.auth.models import User
from django.core import management
from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata

# local Django
from config.settings.base import APPS_DIR
# from apps.api.models import (
#     Person,
#     MedicalRecord,
#     DispensaryRegistration,
#     Anamnesis
# )


class Command(BaseCommand):
    help = 'Creates superuser and populates db with a few object for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Process started'))

        User.objects.filter(email='admin@example.com').delete()
        User.objects.create_superuser('admin', 'admin@example.com', '12345678')
        self.stdout.write(self.style.SUCCESS('Created superuser for testing'))

        # Person.initialize()
        # MedicalRecord.initialize()
        # DispensaryRegistration.initialize()
        # Anamnesis.initialize()
        api_fixtures = os.listdir(os.path.join(APPS_DIR, 'api/fixtures/'))

        management.call_command(loaddata.Command(), *api_fixtures, verbosity=0)
        self.stdout.write(self.style.SUCCESS('Successfully loading fixtures for api'))
