from src.models.audit_log import AuditLog


def create_audit_log(
    db,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | str | None = None,
    details: str | None = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details,
    )

    db.add(audit_log)

    # Do not commit here.
    # The parent business service commits the complete transaction.

    return audit_log


def get_audit_logs(
    db,
    action: str | None = None,
    entity_type: str | None = None,
    user_id: int | None = None,
):
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action)

    if entity_type:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    return query.order_by(
        AuditLog.created_at.desc()
    ).all()