from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from argparse import ArgumentParser


class Command(BaseCommand):
    help = 'Init default superuser'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--username")
        parser.add_argument("--email")
        parser.add_argument("--password")

    def handle(self, *args, **options):
        username = options["username"] or "admin"
        email = options["email"] or "admin@project.com"
        password = options["password"] or username
        try:
            User.objects.create_superuser(username, email, password)
            print("Created: {} : {} : {}".format(username, email, password))
        except Exception:
            print("User {} already exist!".format(username))
