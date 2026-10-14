import json
from datetime import datetime, timezone

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import JSON, JSONB


def serialize_sources(
    column,
    sources,
):
    if isinstance(
        column.type,
        (JSON, JSONB),
    ):
        return sources

    return json.dumps(
        sources,
        default=str,
    )


def log_chat_query(
    database,
    user_id,
    question,
    answer,
    sources,
    confidence,
    model_name,
):
    metadata = MetaData()

    table = Table(
        "chat_query_logs",
        metadata,
        autoload_with=database.bind,
    )

    current_time = datetime.now(
        timezone.utc
    )

    values_by_name = {
        "user_id": user_id,
        "question": question,
        "query": question,
        "query_text": question,
        "answer": answer,
        "response": answer,
        "response_text": answer,
        "confidence": confidence,
        "confidence_score": confidence,
        "model": model_name,
        "model_name": model_name,
        "needs_review": False,
        "created_at": current_time,
        "queried_at": current_time,
        "timestamp": current_time,
    }

    source_column_names = (
        "sources",
        "citations",
        "source_chunks",
        "source_reference",
    )

    insert_values = {}

    for column in table.columns:
        if column.primary_key:
            continue

        if column.name in source_column_names:
            insert_values[column.name] = (
                serialize_sources(
                    column,
                    sources,
                )
            )

        elif column.name in values_by_name:
            insert_values[column.name] = (
                values_by_name[
                    column.name
                ]
            )

    missing_required = []

    for column in table.columns:
        if column.primary_key:
            continue

        if column.name in insert_values:
            continue

        if column.nullable:
            continue

        if column.default is not None:
            continue

        if column.server_default is not None:
            continue

        missing_required.append(
            column.name
        )

    if missing_required:
        print(
            "Chat logging skipped. "
            "Unsupported required columns: "
            + ", ".join(
                missing_required
            )
        )

        return False

    try:
        with database.begin_nested():
            database.execute(
                table.insert().values(
                    **insert_values
                )
            )

        return True

    except Exception as exc:
        print(
            "Chat logging skipped: "
            f"{exc}"
        )

        return False
