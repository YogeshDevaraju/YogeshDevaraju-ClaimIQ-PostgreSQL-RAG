from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.enums import ClaimStatus, PolicyType
from src.db.base import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)

    claim_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    policy_id: Mapped[int] = mapped_column(
        ForeignKey("policies.id"),
        nullable=False,
        index=True,
    )

    claimant_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    claim_type: Mapped[PolicyType] = mapped_column(
        Enum(PolicyType),
        nullable=False,
    )

    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus),
        nullable=False,
        default=ClaimStatus.submitted,
        index=True,
    )

    assigned_adjuster_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    policy = relationship("Policy")
    assigned_adjuster = relationship("User")
    notes = relationship(
        "ClaimNote",
        back_populates="claim",
        cascade="all, delete-orphan",
    )
    status_history = relationship(
        "ClaimStatusHistory",
        back_populates="claim",
        cascade="all, delete-orphan",
    )