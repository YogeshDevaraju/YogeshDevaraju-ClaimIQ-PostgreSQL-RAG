import argparse
import json

from sqlalchemy import inspect, text

from src.db.session import engine


ALIASES = {
    "user": "users",
    "policy": "policies",
    "claim": "claims",
    "document": "documents",
    "doc": "documents",
}


def pretty(value):
    if value is None:
        return "None"

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            indent=2,
            default=str,
            ensure_ascii=False,
        )

    try:
        parsed_value = json.loads(value)

        return json.dumps(
            parsed_value,
            indent=2,
            default=str,
            ensure_ascii=False,
        )

    except (
        TypeError,
        json.JSONDecodeError,
    ):
        return str(value)


def get_available_entities(connection):
    query = text(
        """
        SELECT DISTINCT entity_name
        FROM entity_history
        ORDER BY entity_name
        """
    )

    result = (
        connection.execute(query)
        .scalars()
        .all()
    )

    return list(result)


def run(
    entity,
    entity_id=None,
    operation=None,
    version=None,
    latest=False,
):
    if engine.dialect.name != "postgresql":
        raise SystemExit(
            "This script requires PostgreSQL. "
            f"Current database dialect: "
            f"{engine.dialect.name}"
        )

    normalized_entity = (
        entity.strip().lower()
    )

    entity_name = ALIASES.get(
        normalized_entity,
        normalized_entity,
    )

    if latest and entity_id is None:
        raise SystemExit(
            "ERROR: --latest requires --id.\n"
            "Example: python -m "
            "scripts.history_query "
            "users --id 1 --latest"
        )

    with engine.connect() as connection:
        database_inspector = inspect(
            connection
        )

        if not database_inspector.has_table(
            "entity_history"
        ):
            raise SystemExit(
                "entity_history does not exist. "
                "Run: python -m "
                "scripts.create_all_history"
            )

        available_entities = (
            get_available_entities(
                connection
            )
        )

        if entity_name not in available_entities:
            if available_entities:
                available_text = ", ".join(
                    available_entities
                )
            else:
                available_text = "none"

            raise SystemExit(
                f"No history for '{entity_name}'. "
                f"Available: {available_text}"
            )

        conditions = [
            "entity_name = :entity_name"
        ]

        parameters = {
            "entity_name": entity_name
        }

        if entity_id is not None:
            conditions.append(
                "entity_id = :entity_id"
            )

            parameters["entity_id"] = str(
                entity_id
            )

        if operation is not None:
            conditions.append(
                "operation = :operation"
            )

            parameters["operation"] = (
                operation.upper()
            )

        if version is not None:
            conditions.append(
                "version = :version"
            )

            parameters["version"] = version

        where_clause = " AND ".join(
            conditions
        )

        if latest:
            order_clause = (
                "ORDER BY version DESC "
                "LIMIT 1"
            )
        else:
            order_clause = (
                "ORDER BY "
                "entity_id, version"
            )

        query = text(
            f"""
            SELECT
                history_id,
                entity_name,
                entity_id,
                operation,
                version,
                old_data,
                new_data,
                changed_at
            FROM entity_history
            WHERE {where_clause}
            {order_clause}
            """
        )

        history_rows = (
            connection.execute(
                query,
                parameters,
            )
            .mappings()
            .all()
        )

        print()
        print(
            "CLAIMIQ ENTITY HISTORY"
        )
        print("=" * 100)

        print(
            f"Database        : "
            f"{engine.url.database}"
        )

        print(
            f"Server          : "
            f"{engine.url.host}:"
            f"{engine.url.port}"
        )

        print(
            f"Entity          : "
            f"{entity_name}"
        )

        if entity_id is None:
            entity_id_text = "ALL"
        else:
            entity_id_text = entity_id

        print(
            f"Entity ID       : "
            f"{entity_id_text}"
        )

        if operation is None:
            operation_text = "ALL"
        else:
            operation_text = (
                operation.upper()
            )

        print(
            f"Operation       : "
            f"{operation_text}"
        )

        if version is None:
            version_text = "ALL"
        else:
            version_text = str(version)

        print(
            f"Version         : "
            f"{version_text}"
        )

        if latest:
            latest_text = "YES"
        else:
            latest_text = "NO"

        print(
            f"Latest only     : "
            f"{latest_text}"
        )

        print(
            f"Records returned: "
            f"{len(history_rows)}"
        )

        if not history_rows:
            print(
                "No matching history "
                "records found."
            )
            return

        for history_row in history_rows:
            print()
            print("-" * 100)

            print(
                f"History ID : "
                f"{history_row['history_id']}"
            )

            print(
                f"Entity     : "
                f"{history_row['entity_name']}"
            )

            print(
                f"Entity ID  : "
                f"{history_row['entity_id']}"
            )

            print(
                f"Operation  : "
                f"{history_row['operation']}"
            )

            print(
                f"Version    : "
                f"{history_row['version']}"
            )

            print(
                f"Changed At : "
                f"{history_row['changed_at']}"
            )

            print()
            print("OLD DATA:")

            print(
                pretty(
                    history_row["old_data"]
                )
            )

            print()
            print("NEW DATA:")

            print(
                pretty(
                    history_row["new_data"]
                )
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Read ClaimIQ PostgreSQL "
            "entity version history."
        )
    )

    parser.add_argument(
        "entity",
        help=(
            "Entity such as users, policies, "
            "claims, or documents."
        ),
    )

    parser.add_argument(
        "--id",
        dest="entity_id",
        help=(
            "Optional entity record ID."
        ),
    )

    parser.add_argument(
        "--operation",
        choices=(
            "INSERT",
            "UPDATE",
            "DELETE",
            "insert",
            "update",
            "delete",
        ),
        help=(
            "Optional operation filter."
        ),
    )

    parser.add_argument(
        "--version",
        type=int,
        help=(
            "Optional version number."
        ),
    )

    parser.add_argument(
        "--latest",
        action="store_true",
        help=(
            "Show the latest version. "
            "Requires --id."
        ),
    )

    arguments = parser.parse_args()

    run(
        entity=arguments.entity,
        entity_id=arguments.entity_id,
        operation=arguments.operation,
        version=arguments.version,
        latest=arguments.latest,
    )


if __name__ == "__main__":
    main()