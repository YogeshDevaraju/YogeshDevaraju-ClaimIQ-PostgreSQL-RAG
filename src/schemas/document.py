from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: int
    name: str
    file_path: str
    is_approved: bool
    uploaded_by: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentStatusUpdate(BaseModel):
    is_approved: bool


class DocumentChunkRead(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    section: str | None

    model_config = ConfigDict(from_attributes=True)