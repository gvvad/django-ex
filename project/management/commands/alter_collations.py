from django.core.management.base import BaseCommand
from argparse import ArgumentParser
from django.db import connection


class Command(BaseCommand):
    help = 'Set character and collation for all tables'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--collation")
        parser.add_argument("--character")

    def handle(self, *args, **options):
        collation = options["collation"] or "utf8_general_ci"
        character = options["character"] or "utf8"

        cursor = connection.cursor()
        cursor.execute('SHOW TABLES')
        for row in cursor.fetchall():
            cursor.execute("ALTER TABLE {} CONVERT TO CHARACTER SET {} COLLATE {};".format(
                row[0], character, collation)
            )
