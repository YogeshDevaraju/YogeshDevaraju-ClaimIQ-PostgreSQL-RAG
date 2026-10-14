import sqlite3
from pathlib import Path

from sqlalchemy import inspect

from src.db.session import engine


SQLITE_PATH = (
    Path(__file__).resolve().parent.parent
    / "claimiq_sqlite_backup.db"
)

TABLES = [
    "users",
    "policies",
    "claims",
    "claim_notes",
    "claim_status_history",
    "documents",
    "document_chunks",
    "chat_query_logs",
    "audit_logs",
    "entity_history",
    "user_history",
]


def main():
    if not SQLITE_PATH.exists():
        raise SystemExit(
            f"SQLite backup not found: {SQLITE_PATH}"
        )

    sqlite_connection = sqlite3.connect(
        SQLITE_PATH
    )

    try:
        with engine.connect() as postgres_connection:
            postgres_inspector = inspect(
                postgres_connection
            )

            postgres_tables = set(
                postgres_inspector.get_table_names()
            )

            for table_name in TABLES:
                print()
                print("=" * 100)
                print(f"TABLE: {table_name}")
                print("-" * 100)

                sqlite_exists = sqlite_connection.execute(
                    """
                    SELECT 1
                    FROM sqlite_master
                    WHERE type = 'table'
                      AND name = ?
                    """,
                    (table_name,),
                ).fetchone()

                if sqlite_exists:
                    sqlite_columns = [
                        row[1]
                        for row in sqlite_connection.execute(
                            f'PRAGMA table_info("{table_name}")'
                        ).fetchall()
                    ]

                    print(
                        "SQLite columns    : "
                        + ", ".join(sqlite_columns)
                    )
                else:
                    sqlite_columns = []
                    print("SQLite table      : MISSING")

                if table_name in postgres_tables:
                    postgres_columns = [
                        column["name"]
                        for column
                        in postgres_inspector.get_columns(
                            table_name
                        )
                    ]

                    print(
                        "PostgreSQL columns: "
                        + ", ".join(postgres_columns)
                    )

                    only_sqlite = sorted(
                        set(sqlite_columns)
                        - set(postgres_columns)
                    )

                    only_postgres = sorted(
                        set(postgres_columns)
                        - set(sqlite_columns)
                    )

                    print(
                        "Only in SQLite    : "
                        + (
                            ", ".join(only_sqlite)
                            if only_sqlite
                            else "None"
                        )
                    )

                    print(
                        "Only in PostgreSQL: "
                        + (
                            ", ".join(only_postgres)
                            if only_postgres
                            else "None"
                        )
                    )
                else:
                    print(
                        "PostgreSQL table  : MISSING"
                    )

    finally:
        sqlite_connection.close()


if __name__ == "__main__":
    main()
