import json
import sys

from sqlalchemy import MetaData, Table, inspect, select

from src.db.session import engine


MAXIMUM_COLUMN_WIDTH = 100


def format_value(value):
    if value is None:
        return "None"

    if isinstance(value, (dict, list)):
        text_value = json.dumps(
            value,
            default=str,
            ensure_ascii=False,
        )
    else:
        text_value = str(value)

    text_value = text_value.replace(
        "\r",
        " ",
    )

    text_value = text_value.replace(
        "\n",
        " ",
    )

    if len(text_value) > MAXIMUM_COLUMN_WIDTH:
        return (
            text_value[
                : MAXIMUM_COLUMN_WIDTH - 3
            ]
            + "..."
        )

    return text_value


def get_available_tables(connection):
    database_inspector = inspect(
        connection
    )

    return sorted(
        database_inspector.get_table_names()
    )


def view_table(table_name):
    if engine.dialect.name != "postgresql":
        raise SystemExit(
            "This script requires PostgreSQL. "
            f"Current database dialect: "
            f"{engine.dialect.name}"
        )

    with engine.connect() as connection:
        available_tables = (
            get_available_tables(
                connection
            )
        )

        if table_name not in available_tables:
            print()

            print(
                f"Table '{table_name}' "
                f"does not exist."
            )

            print()
            print("Available tables:")

            for available_table in (
                available_tables
            ):
                print(
                    f"  - {available_table}"
                )

            return

        metadata = MetaData()

        selected_table = Table(
            table_name,
            metadata,
            autoload_with=connection,
        )

        query = select(
            selected_table
        )

        primary_key_columns = list(
            selected_table.primary_key.columns
        )

        if primary_key_columns:
            query = query.order_by(
                *primary_key_columns
            )

        result = connection.execute(
            query
        )

        column_names = list(
            result.keys()
        )

        database_rows = (
            result.mappings().all()
        )

        print()

        print(
            f"Database: "
            f"{engine.url.database}"
        )

        print(
            f"Server: "
            f"{engine.url.host}:"
            f"{engine.url.port}"
        )

        print(
            f"Table: {table_name}"
        )

        print(
            f"Row count: "
            f"{len(database_rows)}"
        )

        print()

        if not database_rows:
            print("No rows found.")
            return

        formatted_rows = []

        for database_row in database_rows:
            formatted_row = []

            for column_name in column_names:
                formatted_row.append(
                    format_value(
                        database_row[
                            column_name
                        ]
                    )
                )

            formatted_rows.append(
                formatted_row
            )

        column_widths = []

        for position, column_name in enumerate(
            column_names
        ):
            widest_value = max(
                len(
                    row[position]
                )
                for row in formatted_rows
            )

            column_width = min(
                max(
                    len(column_name),
                    widest_value,
                ),
                MAXIMUM_COLUMN_WIDTH,
            )

            column_widths.append(
                column_width
            )

        header = " | ".join(
            column_name.ljust(
                column_widths[position]
            )
            for position, column_name
            in enumerate(column_names)
        )

        separator = "-+-".join(
            "-" * column_width
            for column_width
            in column_widths
        )

        print(header)
        print(separator)

        for formatted_row in formatted_rows:
            output_line = " | ".join(
                formatted_row[position].ljust(
                    column_widths[position]
                )
                for position in range(
                    len(column_names)
                )
            )

            print(output_line)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m "
            "scripts.view_table "
            "<table_name>"
        )

        print()
        print("Examples:")

        print(
            "  python -m "
            "scripts.view_table users"
        )

        print(
            "  python -m "
            "scripts.view_table policies"
        )

        print(
            "  python -m "
            "scripts.view_table claims"
        )

        print(
            "  python -m "
            "scripts.view_table documents"
        )

        print(
            "  python -m "
            "scripts.view_table "
            "document_chunks"
        )

        print(
            "  python -m "
            "scripts.view_table "
            "claim_status_history"
        )

        print(
            "  python -m "
            "scripts.view_table "
            "chat_query_logs"
        )

        print(
            "  python -m "
            "scripts.view_table "
            "audit_logs"
        )

        print(
            "  python -m "
            "scripts.view_table "
            "entity_history"
        )

        return

    table_name = sys.argv[1].strip()

    view_table(
        table_name
    )


if __name__ == "__main__":
    main()