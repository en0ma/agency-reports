from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from warehouse.loader import load_warehouse


class Command(BaseCommand):
    help = "Rebuilds the local warehouse database from data/warehouse/schema.sql and its CSV part files."

    def handle(self, *args: object, **options: object) -> None:
        db_path = settings.DATABASES["default"]["NAME"]
        connection.close()
        db_path.unlink(missing_ok=True)

        counts = load_warehouse(connection, settings.WAREHOUSE_DATA_DIR)
        for table, rows in counts.items():
            self.stdout.write(f"  {table}: {rows:,} rows")
        self.stdout.write(self.style.SUCCESS(f"Warehouse built at {db_path}"))
