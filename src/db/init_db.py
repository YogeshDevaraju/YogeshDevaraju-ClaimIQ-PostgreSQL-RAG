from src.db.base import Base
from src.db.session import engine

# These imports register every model with Base.metadata.
from src.models.audit_log import AuditLog
from src.models.chat_query_log import ChatQueryLog
from src.models.claim import Claim
from src.models.claim_note import ClaimNote
from src.models.claim_status_history import (
    ClaimStatusHistory,
)
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.models.policy import Policy
from src.models.user import User


def init_db() -> None:
    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Database tables created successfully:"
    )

    for table_name in sorted(
        Base.metadata.tables.keys()
    ):
        print(
            f"  - {table_name}"
        )


if __name__ == "__main__":
    init_db()