from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import MetaData, Table, select, update
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.chat_review import (
    ChatReviewRequest,
    ChatReviewResponse,
)


router = APIRouter(
    prefix="/chat/logs",
    tags=["RAG Chat Review"],
)


@router.patch(
    "/{log_id}/review",
    response_model=ChatReviewResponse,
)
def update_review_status(
    log_id: int,
    request: ChatReviewRequest,
    database: Session = Depends(get_db),
):
    metadata = MetaData()

    table = Table(
        "chat_query_logs",
        metadata,
        autoload_with=database.bind,
    )

    existing_log = database.execute(
        select(table.c.id).where(
            table.c.id == log_id
        )
    ).first()

    if existing_log is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chat query log {log_id} was not found.",
        )

    database.execute(
        update(table)
        .where(table.c.id == log_id)
        .values(
            needs_review=request.needs_review
        )
    )

    database.commit()

    return ChatReviewResponse(
        id=log_id,
        needs_review=request.needs_review,
        message="Review status updated successfully.",
    )
