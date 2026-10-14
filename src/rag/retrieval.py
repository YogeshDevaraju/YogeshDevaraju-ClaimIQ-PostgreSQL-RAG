from sqlalchemy import select

from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.rag.embeddings import embed_text


DEFAULT_TOP_K = 5
MAXIMUM_TOP_K = 20


def retrieve_chunks(
    database,
    question,
    top_k=DEFAULT_TOP_K,
    include_inactive=False,
):
    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1."
        )

    if top_k > MAXIMUM_TOP_K:
        raise ValueError(
            f"top_k cannot exceed {MAXIMUM_TOP_K}."
        )

    question_embedding = embed_text(
        question
    )

    cosine_distance = (
        DocumentChunk.embedding
        .cosine_distance(
            question_embedding
        )
    )

    similarity = (
        1 - cosine_distance
    ).label("similarity")

    query = (
        select(
            DocumentChunk.id.label(
                "chunk_id"
            ),
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
            DocumentChunk.section,
            DocumentChunk.content,
            Document.name.label(
                "document_name"
            ),
            Document.file_path,
            Document.is_approved,
            similarity,
        )
        .join(
            Document,
            Document.id
            == DocumentChunk.document_id,
        )
        .where(
            DocumentChunk.embedding
            .is_not(None)
        )
    )

    if not include_inactive:
        query = query.where(
            Document.is_approved.is_(True)
        )

    query = (
        query
        .order_by(cosine_distance)
        .limit(top_k)
    )

    rows = (
        database.execute(query)
        .mappings()
        .all()
    )

    results = []

    for row in rows:
        results.append(
            {
                "document_id": row[
                    "document_id"
                ],
                "document_name": row[
                    "document_name"
                ],
                "file_path": row[
                    "file_path"
                ],
                "chunk_id": row[
                    "chunk_id"
                ],
                "chunk_index": row[
                    "chunk_index"
                ],
                "section": row[
                    "section"
                ],
                "content": row[
                    "content"
                ],
                "similarity": round(
                    float(
                        row["similarity"]
                    ),
                    6,
                ),
                "is_approved": bool(
                    row["is_approved"]
                ),
            }
        )

    return results
