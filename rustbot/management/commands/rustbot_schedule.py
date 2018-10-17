from django.core.management.base import BaseCommand
from django.apps import apps

app = apps.get_app_config("rustbot")


class Command(BaseCommand):
    help = 'Rus tbot Schedule update'

    def handle(self, *args, **options):
        app.run_schedule()
