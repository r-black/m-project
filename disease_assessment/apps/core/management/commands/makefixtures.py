# standard library
import json
import os

# Django
from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand

# local Django
from config.settings.base import APPS_DIR


class Command(BaseCommand):
    help = 'Creates fixtures for models in local apps'

    def write_json_from_queryset(self, queryset, app_label, model_name):
        data = json.loads(serializers.serialize('json', queryset))
        filename = os.path.join(APPS_DIR, '%s/fixtures/%s.json' % (app_label, model_name))
        try:
            with open(filename, 'w', encoding='utf-8', newline='\n') as json_file:
                json.dump(data, json_file, indent=2, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS('Successfully create fixture for %s' % model_name))
        except (PermissionError, FileNotFoundError) as e:
            self.stdout.write(self.style.ERROR('%s' % e))

    def handle(self, *args, **options):
        app_labels = ('api',)
        for app_label in app_labels:
            app = apps.get_app_config(app_label)
            app_models = app.get_models()
            for model in app_models:
                self.write_json_from_queryset(model.objects.order_by('pk'), app_label, model.__name__.lower())
