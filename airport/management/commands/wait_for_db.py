import time

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Wait for database to be available."""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")

        while True:
            try:
                connection.ensure_connection()
            except OperationalError:
                self.stdout.write("Database unavailable, waiting...")
                time.sleep(1)
            else:
                break

        self.stdout.write(
            self.style.SUCCESS("Database available!")
        )
