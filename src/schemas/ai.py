from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIQueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=5,
    )


class AISource(BaseModel):
    document_id: int
    document: str
    section: str
    score: float


class AIQueryResponse(BaseModel):
    answer: str
    sources: list[AISource]
    confidence: float
    needs_review: bool


class AIQueryLogRead(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str
    source_reference: str | None
    confidence: float
    needs_review: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)