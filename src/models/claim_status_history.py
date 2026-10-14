from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.enums import ClaimStatus
from src.db.base import Base


class ClaimStatusHistory(Base):
    __tablename__ = "claim_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[ClaimStatus | None] = mapped_column(
        Enum(ClaimStatus),
        nullable=True,
    )

    new_status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus),
        nullable=False,
    )

    changed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    justification: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    claim = relationship(
        "Claim",
        back_populates="status_history",
    )

    user = relationship("User")