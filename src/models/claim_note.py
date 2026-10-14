from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class ClaimNote(Base):
    __tablename__ = "claim_notes"

    id: Mapped[int] = mapped_column(primary_key=True)

    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    note: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    claim = relationship(
        "Claim",
        back_populates="notes",
    )

    user = relationship("User")