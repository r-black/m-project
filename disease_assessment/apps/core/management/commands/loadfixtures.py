# standard library
import os

# Django
from django.core import management
from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata

# local Django
from config.settings.base import APPS_DIR


class Command(BaseCommand):
    help = 'Load fixtures for models in local apps'

    def handle(self, *args, **options):
        fixtures = os.listdir(os.path.join(APPS_DIR, 'api/fixtures/'))

        management.call_command(loaddata.Command(), *fixtures, verbosity=0)
        self.stdout.write(self.style.SUCCESS('Successfully loading fixtures for api'))
