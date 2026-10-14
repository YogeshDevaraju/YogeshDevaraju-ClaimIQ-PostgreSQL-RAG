from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.common.enums import ClaimStatus
from src.db.session import get_db
from src.schemas.claim import (
    ClaimCreate,
    ClaimHistoryRead,
    ClaimNoteCreate,
    ClaimNoteRead,
    ClaimRead,
    ClaimStatusUpdate,
    ClaimUpdate,
)
from src.services import claim_service

# Change this import if your project uses a different
# authentication dependency.
from src.api.dependencies import get_current_user


router = APIRouter(
    prefix="/claims",
    tags=["Claims"],
)


@router.post(
    "",
    response_model=ClaimRead,
    status_code=status.HTTP_201_CREATED,
)
def create_claim(
    payload: ClaimCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.create_claim(
        payload,
        current_user,
        db,
    )


@router.get(
    "",
    response_model=list[ClaimRead],
)
def list_claims(
    policy_id: int | None = None,
    claimant_name: str | None = None,
    status_value: ClaimStatus | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.get_claims(
        db=db,
        current_user=current_user,
        policy_id=policy_id,
        claimant_name=claimant_name,
        status=status_value,
        region=region,
    )


@router.get(
    "/{claim_id}",
    response_model=ClaimRead,
)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.get_claim_by_id(
        claim_id,
        db,
    )


@router.patch(
    "/{claim_id}",
    response_model=ClaimRead,
)
def update_claim(
    claim_id: int,
    payload: ClaimUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.update_claim(
        claim_id,
        payload,
        current_user,
        db,
    )


@router.patch(
    "/{claim_id}/status",
    response_model=ClaimRead,
)
def update_status(
    claim_id: int,
    payload: ClaimStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.update_claim_status(
        claim_id,
        payload,
        current_user,
        db,
    )


@router.post(
    "/{claim_id}/notes",
    response_model=ClaimNoteRead,
    status_code=status.HTTP_201_CREATED,
)
def add_note(
    claim_id: int,
    payload: ClaimNoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.add_claim_note(
        claim_id,
        payload,
        current_user,
        db,
    )


@router.get(
    "/{claim_id}/notes",
    response_model=list[ClaimNoteRead],
)
def get_notes(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.get_claim_notes(
        claim_id,
        db,
    )


@router.get(
    "/{claim_id}/history",
    response_model=list[ClaimHistoryRead],
)
def get_history(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return claim_service.get_claim_history(
        claim_id,
        db,
    )