from datetime import UTC, datetime

from fastapi import HTTPException

from src.common.enums import (
    ClaimStatus,
    PolicyStatus,
    UserRole,
)
from src.models.claim import Claim
from src.models.claim_note import ClaimNote
from src.models.claim_status_history import (
    ClaimStatusHistory,
)
from src.models.policy import Policy
from src.models.user import User
from src.services.audit_service import create_audit_log


VALID_TRANSITIONS = {
    ClaimStatus.submitted: {
        ClaimStatus.under_review,
    },
    ClaimStatus.under_review: {
        ClaimStatus.approved,
        ClaimStatus.rejected,
    },
    ClaimStatus.approved: {
        ClaimStatus.closed,
    },
    ClaimStatus.rejected: {
        ClaimStatus.closed,
    },
    ClaimStatus.closed: set(),
}


def generate_claim_number(db) -> str:
    year = datetime.now().year

    latest_claim = (
        db.query(Claim)
        .order_by(Claim.id.desc())
        .first()
    )

    if not latest_claim:
        sequence = 1
    else:
        try:
            sequence = (
                int(
                    latest_claim.claim_number.split("-")[-1]
                )
                + 1
            )
        except (ValueError, IndexError):
            sequence = latest_claim.id + 1

    return f"CLM-{year}-{sequence:06d}"


def get_claim_by_id(
    claim_id: int,
    db,
) -> Claim:
    claim = (
        db.query(Claim)
        .filter(Claim.id == claim_id)
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )

    return claim


def validate_active_policy(
    policy_id: int,
    db,
) -> Policy:
    policy = (
        db.query(Policy)
        .filter(Policy.id == policy_id)
        .first()
    )

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Policy not found",
        )

    if policy.status != PolicyStatus.active:
        raise HTTPException(
            status_code=422,
            detail="Claim must be linked to an active policy",
        )

    return policy


def validate_adjuster(
    adjuster_id: int | None,
    db,
):
    if adjuster_id is None:
        return None

    adjuster = (
        db.query(User)
        .filter(
            User.id == adjuster_id,
            User.is_active.is_(True),
        )
        .first()
    )

    if not adjuster:
        raise HTTPException(
            status_code=404,
            detail="Assigned adjuster not found",
        )

    if adjuster.role not in {
        UserRole.claims_adjuster,
        UserRole.claims_adjuster.value,
    }:
        raise HTTPException(
            status_code=422,
            detail="Assigned user must be a Claims Adjuster",
        )

    return adjuster


def create_claim(
    payload,
    current_user,
    db,
):
    validate_active_policy(payload.policy_id, db)

    validate_adjuster(
        payload.assigned_adjuster_id,
        db,
    )

    claim = Claim(
        claim_number=generate_claim_number(db),
        policy_id=payload.policy_id,
        claimant_name=payload.claimant_name,
        claim_type=payload.claim_type,
        region=payload.region,
        amount=payload.amount,
        assigned_adjuster_id=(
            payload.assigned_adjuster_id
        ),
        status=ClaimStatus.submitted,
    )

    db.add(claim)
    db.flush()

    history = ClaimStatusHistory(
        claim_id=claim.id,
        old_status=None,
        new_status=ClaimStatus.submitted,
        changed_by=current_user.id,
        justification="Claim created",
    )

    db.add(history)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CLAIM_CREATED",
        entity_type="Claim",
        entity_id=claim.id,
        details=(
            f"Claim {claim.claim_number} created "
            f"with SUBMITTED status"
        ),
    )

    db.commit()
    db.refresh(claim)

    return claim


def get_claims(
    db,
    current_user,
    policy_id: int | None = None,
    claimant_name: str | None = None,
    status: ClaimStatus | None = None,
    region: str | None = None,
):
    query = db.query(Claim)

    user_role = current_user.role

    if user_role in {
        UserRole.claims_adjuster,
        UserRole.claims_adjuster.value,
    }:
        query = query.filter(
            (Claim.assigned_adjuster_id == current_user.id)
            | (Claim.region == getattr(
                current_user,
                "region",
                None,
            ))
        )

    if policy_id:
        query = query.filter(
            Claim.policy_id == policy_id
        )

    if claimant_name:
        query = query.filter(
            Claim.claimant_name.ilike(
                f"%{claimant_name}%"
            )
        )

    if status:
        query = query.filter(
            Claim.status == status
        )

    if region:
        query = query.filter(
            Claim.region == region
        )

    return query.order_by(
        Claim.submitted_at.desc()
    ).all()


def update_claim(
    claim_id: int,
    payload,
    current_user,
    db,
):
    claim = get_claim_by_id(claim_id, db)

    if payload.claimant_name is not None:
        claim.claimant_name = payload.claimant_name

    if payload.region is not None:
        claim.region = payload.region

    if payload.amount is not None:
        claim.amount = payload.amount

    if payload.assigned_adjuster_id is not None:
        validate_adjuster(
            payload.assigned_adjuster_id,
            db,
        )
        claim.assigned_adjuster_id = (
            payload.assigned_adjuster_id
        )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CLAIM_UPDATED",
        entity_type="Claim",
        entity_id=claim.id,
        details="Claim information updated",
    )

    db.commit()
    db.refresh(claim)

    return claim


def update_claim_status(
    claim_id: int,
    payload,
    current_user,
    db,
):
    claim = get_claim_by_id(claim_id, db)

    old_status = claim.status
    new_status = payload.status

    allowed_statuses = VALID_TRANSITIONS.get(
        old_status,
        set(),
    )

    is_manager = current_user.role in {
        UserRole.claims_manager,
        UserRole.claims_manager.value,
    }

    manager_override_allowed = (
        payload.manager_override
        and is_manager
        and bool(payload.justification)
    )

    if (
        new_status not in allowed_statuses
        and not manager_override_allowed
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Invalid status transition: "
                f"{old_status.value} to {new_status.value}"
            ),
        )

    claim.status = new_status
    claim.updated_at = datetime.now(UTC)

    if new_status == ClaimStatus.closed:
        claim.closed_at = datetime.now(UTC)

    history = ClaimStatusHistory(
        claim_id=claim.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        justification=payload.justification,
    )

    db.add(history)

    if payload.note:
        note = ClaimNote(
            claim_id=claim.id,
            user_id=current_user.id,
            note=payload.note,
        )
        db.add(note)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CLAIM_STATUS_CHANGED",
        entity_type="Claim",
        entity_id=claim.id,
        details=(
            f"{old_status.value} -> "
            f"{new_status.value}"
        ),
    )

    db.commit()
    db.refresh(claim)

    return claim


def add_claim_note(
    claim_id: int,
    payload,
    current_user,
    db,
):
    get_claim_by_id(claim_id, db)

    note = ClaimNote(
        claim_id=claim_id,
        user_id=current_user.id,
        note=payload.note,
    )

    db.add(note)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CLAIM_NOTE_ADDED",
        entity_type="Claim",
        entity_id=claim_id,
        details="A claim note was added",
    )

    db.commit()
    db.refresh(note)

    return note


def get_claim_notes(
    claim_id: int,
    db,
):
    get_claim_by_id(claim_id, db)

    return (
        db.query(ClaimNote)
        .filter(ClaimNote.claim_id == claim_id)
        .order_by(ClaimNote.created_at.desc())
        .all()
    )


def get_claim_history(
    claim_id: int,
    db,
):
    get_claim_by_id(claim_id, db)

    return (
        db.query(ClaimStatusHistory)
        .filter(
            ClaimStatusHistory.claim_id == claim_id
        )
        .order_by(
            ClaimStatusHistory.changed_at.asc()
        )
        .all()
    )