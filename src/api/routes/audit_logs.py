from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.schemas.audit_log import AuditLogRead
from src.services.audit_service import get_audit_logs


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=list[AuditLogRead],
)
def list_audit_logs(
    action: str | None = None,
    entity_type: str | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_audit_logs(
        db=db,
        action=action,
        entity_type=entity_type,
        user_id=user_id,
    )