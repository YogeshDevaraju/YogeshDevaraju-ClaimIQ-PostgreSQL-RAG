from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.db.session import get_db
from src.schemas.document import (
    DocumentChunkRead,
    DocumentRead,
    DocumentStatusUpdate,
)
from src.services import document_service


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return document_service.upload_document(
        file,
        current_user,
        db,
    )


@router.get(
    "",
    response_model=list[DocumentRead],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return document_service.get_documents(db)


@router.patch(
    "/{document_id}/status",
    response_model=DocumentRead,
)
def update_status(
    document_id: int,
    payload: DocumentStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return document_service.update_document_status(
        document_id,
        payload,
        current_user,
        db,
    )


@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkRead],
)
def list_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return document_service.get_document_chunks(
        document_id,
        db,
    )