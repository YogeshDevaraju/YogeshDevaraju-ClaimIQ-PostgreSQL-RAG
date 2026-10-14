import re
import time
from pathlib import Path

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from src.core.config import settings
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.services.audit_service import create_audit_log


ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def clean_file_name(file_name: str) -> str:
    return re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        file_name,
    )


def split_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 150,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    result = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            result.append(chunk)

        start += chunk_size - overlap

    return result


def extract_text(file_path: Path) -> str:
    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    try:
        reader = PdfReader(str(file_path))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="PDF could not be processed",
        ) from exc


def upload_document(
    upload_file: UploadFile,
    current_user,
    db,
):
    original_name = upload_file.filename or "document"
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Only PDF and TXT documents are allowed",
        )

    document_directory = Path(settings.document_dir)

    document_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = clean_file_name(original_name)
    stored_name = f"{int(time.time())}_{safe_name}"
    file_path = document_directory / stored_name

    try:
        file_content = upload_file.file.read()

        if not file_content:
            raise HTTPException(
                status_code=422,
                detail="Uploaded document is empty",
            )

        file_path.write_bytes(file_content)

        text = extract_text(file_path)

        if not text.strip():
            file_path.unlink(missing_ok=True)

            raise HTTPException(
                status_code=422,
                detail="Document contains no extractable text",
            )

        document = Document(
            name=original_name,
            file_path=str(file_path),
            is_approved=True,
            uploaded_by=current_user.id,
        )

        db.add(document)
        db.flush()

        text_chunks = split_text(text)

        for index, chunk_text in enumerate(text_chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
                section=f"chunk-{index}",
            )

            db.add(chunk)

        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="DOCUMENT_UPLOADED",
            entity_type="Document",
            entity_id=document.id,
            details=f"{len(text_chunks)} chunks created",
        )

        db.commit()
        db.refresh(document)

        return document

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Document upload failed",
        ) from exc


def get_documents(db):
    return (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


def get_document_by_id(
    document_id: int,
    db,
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


def update_document_status(
    document_id: int,
    payload,
    current_user,
    db,
):
    document = get_document_by_id(
        document_id,
        db,
    )

    try:
        document.is_approved = payload.is_approved

        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="DOCUMENT_STATUS_CHANGED",
            entity_type="Document",
            entity_id=document.id,
            details=f"is_approved={payload.is_approved}",
        )

        db.commit()
        db.refresh(document)

        return document

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Document status update failed",
        ) from exc


def get_document_chunks(
    document_id: int,
    db,
):
    get_document_by_id(
        document_id,
        db,
    )

    return (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id
        )
        .order_by(
            DocumentChunk.chunk_index.asc()
        )
        .all()
    )