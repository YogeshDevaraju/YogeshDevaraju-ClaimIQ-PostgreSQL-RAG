from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user import User


def get_current_user(
    x_user_id: int = Header(
        ...,
        description="ID of the current user",
    ),
    db: Session = Depends(get_db),
) -> User:
    user = (
        db.query(User)
        .filter(
            User.id == x_user_id,
            User.is_active.is_(True),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Active user not found",
        )

    return user