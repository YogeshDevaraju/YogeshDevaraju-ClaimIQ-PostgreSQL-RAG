import sqlite3
from pathlib import Path


database_path = Path("claimiq_sqlite_backup.db")

if not database_path.exists():
    raise SystemExit(
        f"SQLite backup not found: {database_path.resolve()}"
    )


connection = sqlite3.connect(database_path)

try:
    tables = [
        record[0]
        for record in connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
    ]

    print()
    print("SQLITE SOURCE COUNTS")
    print("=" * 60)

    for table_name in tables:
        quoted_name = (
            '"'
            + table_name.replace('"', '""')
            + '"'
        )

        row_count = connection.execute(
            f"SELECT COUNT(*) FROM {quoted_name}"
        ).fetchone()[0]

        print(
            f"{table_name:<30} {row_count}"
        )

finally:
    connection.close()
