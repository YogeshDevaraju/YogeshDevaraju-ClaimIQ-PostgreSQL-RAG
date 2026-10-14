from sqlalchemy import inspect, text

from src.db.session import engine


DESCRIPTIONS = {
    "users": "Application users, roles, email, and active status.",
    "policies": "Insurance policies, coverage, dates, regions, and status.",
    "claims": "Claims, amounts, workflow status, policy, and adjuster.",
    "claim_notes": "Notes recorded during claim processing.",
    "claim_status_history": "Append-only claim status transitions.",
    "documents": "Uploaded document metadata and approval status.",
    "document_chunks": "Document text chunks used for retrieval and RAG.",
    "chat_query_logs": "AI questions, answers, sources, and confidence.",
    "audit_logs": "Application audit activity.",
    "entity_history": "INSERT, UPDATE, and DELETE row versions.",
}


def quote_identifier(name):
    return engine.dialect.identifier_preparer.quote(name)


def main():
    if engine.dialect.name != "postgresql":
        raise SystemExit(
            "This script requires PostgreSQL. "
            f"Current database dialect: {engine.dialect.name}"
        )

    with engine.connect() as connection:
        database_inspector = inspect(connection)

        table_names = sorted(
            database_inspector.get_table_names()
        )

        print()
        print("AVAILABLE CLAIMIQ ENTITIES")
        print("=" * 120)
        print(
            f"{'ENTITY':<25} "
            f"{'ROWS':<10} "
            f"PURPOSE"
        )
        print("-" * 120)

        for table_name in table_names:
            quoted_table = quote_identifier(
                table_name
            )

            count_query = text(
                f"SELECT COUNT(*) "
                f"FROM {quoted_table}"
            )

            row_count = connection.execute(
                count_query
            ).scalar_one()

            purpose = DESCRIPTIONS.get(
                table_name,
                "Application database table.",
            )

            print(
                f"{table_name:<25} "
                f"{row_count:<10} "
                f"{purpose}"
            )

        print()
        print(
            f"Database: {engine.url.database}"
        )
        print(
            f"Server: "
            f"{engine.url.host}:"
            f"{engine.url.port}"
        )
        print(
            f"Total entities: {len(table_names)}"
        )


if __name__ == "__main__":
    main()
