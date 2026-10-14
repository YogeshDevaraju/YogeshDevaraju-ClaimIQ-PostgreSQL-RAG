from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.schemas.ai import (
    AIQueryLogRead,
    AIQueryRequest,
    AIQueryResponse,
)
from src.services import ai_service


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/query",
    response_model=AIQueryResponse,
)
def ask_question(
    payload: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ai_service.ask_question(
        payload,
        current_user,
        db,
    )


@router.get(
    "/query-logs",
    response_model=list[AIQueryLogRead],
)
def list_query_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ai_service.get_query_logs(db)