"""Builds the local stand-in for the warehouse: runs schema.sql, then loads every CSV part file under
`<data_dir>/<table>/` into that table, the same way a Delta table is a folder of part files.
"""

import csv
from pathlib import Path

from django.db import transaction
from django.db.backends.base.base import BaseDatabaseWrapper


def load_warehouse(connection: BaseDatabaseWrapper, data_dir: Path, schema_file: Path | None = None) -> dict[str, int]:
    schema_sql = (schema_file or data_dir / "schema.sql").read_text(encoding="utf-8")
    counts: dict[str, int] = {}

    # One transaction for the whole load. Without it, SQLite commits (and syncs to disk) after every row.
    with transaction.atomic(using=connection.alias), connection.cursor() as cursor:
        for statement in _statements(schema_sql):
            cursor.execute(statement)

        # Load in the order schema.sql creates the tables, so foreign keys always point at rows already loaded.
        tables = [_created_table(statement) for statement in _statements(schema_sql)]
        tables = [table for table in tables if table]

        for table in tables:
            counts[table] = 0
            for part in sorted((data_dir / table).glob("*.csv")):
                with part.open(newline="", encoding="utf-8") as handle:
                    reader = csv.reader(handle)
                    columns = next(reader, None)
                    if not columns:
                        continue
                    placeholders = ", ".join(["%s"] * len(columns))
                    rows = [[value if value != "" else None for value in row] for row in reader if row]
                    cursor.executemany(
                        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                        rows,
                    )
                    counts[table] += len(rows)
    return counts


def _created_table(statement: str) -> str | None:
    words = statement.split()
    if len(words) >= 3 and [w.upper() for w in words[:2]] == ["CREATE", "TABLE"]:
        return words[2]
    return None


def _statements(sql: str) -> list[str]:
    without_comments = "\n".join(line.split("--", 1)[0] for line in sql.splitlines())
    return [statement.strip() for statement in without_comments.split(";") if statement.strip()]
