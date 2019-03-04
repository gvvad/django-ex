from django.core.management.base import BaseCommand
from django.apps import apps

app = apps.get_app_config("tolokatbot")


class Command(BaseCommand):
    help = 'Rus tbot set webhook'

    def handle(self, *args, **options):
        app.set_webhook()
