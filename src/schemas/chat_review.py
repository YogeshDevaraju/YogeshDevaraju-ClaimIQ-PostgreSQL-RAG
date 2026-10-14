from pydantic import BaseModel


class ChatReviewRequest(BaseModel):
    needs_review: bool


class ChatReviewResponse(BaseModel):
    id: int
    needs_review: bool
    message: str
