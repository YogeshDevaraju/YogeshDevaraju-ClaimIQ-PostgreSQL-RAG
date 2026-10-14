from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.rag.service import answer_question
from src.schemas.rag_chat import (
    ChatQueryRequest,
    ChatQueryResponse,
)


router = APIRouter(
    prefix="/chat",
    tags=["RAG Chat"],
)


@router.post(
    "/query",
    response_model=ChatQueryResponse,
)
def query_claimiq(
    request: ChatQueryRequest,
    database: Session = Depends(get_db),
):
    try:
        result = answer_question(
            database=database,
            user_id=request.user_id,
            question=request.question,
            top_k=request.top_k,
            include_inactive=(
                request.include_inactive
            ),
        )

        return ChatQueryResponse(
            **result
        )

    except ValueError as exc:
        database.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        database.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "ClaimIQ RAG query failed: "
                f"{exc}"
            ),
        ) from exc
