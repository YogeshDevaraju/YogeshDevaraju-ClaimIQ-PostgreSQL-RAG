from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.services.analytics_service import (
    get_claim_analytics,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/claims")
def claim_analytics(
    region: str | None = None,
    claim_type: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_claim_analytics(
        db=db,
        region=region,
        claim_type=claim_type,
    )