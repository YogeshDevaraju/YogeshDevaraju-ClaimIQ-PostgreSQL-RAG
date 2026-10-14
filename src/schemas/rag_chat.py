from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    include_inactive: bool = False

    user_id: int = Field(
        ge=1,
    )


class SourceCitation(BaseModel):
    document_id: int
    document_name: str
    chunk_id: int
    chunk_index: int
    section: str | None = None
    similarity: float


class ChatQueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    confidence: float | None = None
    retrieval_count: int
    llm_used: bool
    logged: bool
