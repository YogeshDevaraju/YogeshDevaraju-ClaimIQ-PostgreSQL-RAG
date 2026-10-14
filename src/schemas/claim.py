from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.common.enums import ClaimStatus, PolicyType
from src.common.validators import clean_string


class ClaimCreate(BaseModel):
    policy_id: int = Field(gt=0)
    claimant_name: str = Field(min_length=2, max_length=120)
    claim_type: PolicyType
    region: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0)
    assigned_adjuster_id: int | None = Field(default=None, gt=0)

    @field_validator("claimant_name", "region")
    @classmethod
    def clean_text_fields(cls, value: str) -> str:
        return clean_string(value)


class ClaimRead(BaseModel):
    id: int
    claim_number: str
    policy_id: int
    claimant_name: str
    claim_type: PolicyType
    region: str
    amount: Decimal
    status: ClaimStatus
    assigned_adjuster_id: int | None
    submitted_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ClaimUpdate(BaseModel):
    claimant_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )
    region: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    amount: Decimal | None = Field(default=None, gt=0)
    assigned_adjuster_id: int | None = Field(default=None, gt=0)

    @field_validator("claimant_name", "region")
    @classmethod
    def clean_optional_text(cls, value: str | None):
        if value is None:
            return value

        return clean_string(value)


class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
    note: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
    )
    manager_override: bool = False
    justification: str | None = Field(
        default=None,
        max_length=2000,
    )


class ClaimNoteCreate(BaseModel):
    note: str = Field(
        min_length=1,
        max_length=2000,
    )


class ClaimNoteRead(BaseModel):
    id: int
    claim_id: int
    user_id: int
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimHistoryRead(BaseModel):
    id: int
    claim_id: int
    old_status: ClaimStatus | None
    new_status: ClaimStatus
    changed_by: int
    justification: str | None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)