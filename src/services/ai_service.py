import re

from src.models.chat_query_log import ChatQueryLog
from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.services.audit_service import create_audit_log


def extract_terms(text: str) -> set[str]:
    return {
        word.lower()
        for word in re.findall(
            r"[A-Za-z]{3,}",
            text,
        )
    }


def calculate_score(
    question_terms: set[str],
    content: str,
) -> float:
    if not question_terms:
        return 0.0

    content_terms = extract_terms(content)

    matching_terms = (
        question_terms.intersection(content_terms)
    )

    return len(matching_terms) / len(question_terms)


def retrieve_chunks(
    question: str,
    top_k: int,
    db,
):
    question_terms = extract_terms(question)

    rows = (
        db.query(DocumentChunk, Document)
        .join(
            Document,
            Document.id
            == DocumentChunk.document_id,
        )
        .filter(Document.is_approved.is_(True))
        .all()
    )

    results = []

    for chunk, document in rows:
        score = calculate_score(
            question_terms,
            chunk.content,
        )

        if score > 0:
            results.append(
                {
                    "score": score,
                    "chunk": chunk,
                    "document": document,
                }
            )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]


def ask_question(
    payload,
    current_user,
    db,
):
    matches = retrieve_chunks(
        payload.question,
        payload.top_k,
        db,
    )

    if not matches:
        answer = (
            "No relevant information was found "
            "in the approved documents."
        )

        query_log = ChatQueryLog(
            user_id=current_user.id,
            question=payload.question,
            answer=answer,
            source_reference=None,
            confidence=0,
            needs_review=True,
        )

        db.add(query_log)

        create_audit_log(
            db=db,
            user_id=current_user.id,
            action="AI_QUERY_NO_MATCH",
            entity_type="ChatQueryLog",
            details="No approved source matched",
        )

        db.commit()

        return {
            "answer": answer,
            "sources": [],
            "confidence": 0,
            "needs_review": True,
        }

    sources = []
    selected_content = []

    for result in matches:
        chunk = result["chunk"]
        document = result["document"]

        selected_content.append(chunk.content[:600])

        sources.append(
            {
                "document_id": document.id,
                "document": document.name,
                "section": (
                    chunk.section
                    or f"chunk-{chunk.chunk_index}"
                ),
                "score": round(
                    result["score"],
                    3,
                ),
            }
        )

    answer = (
        "Based on the approved policy documents: "
        + " ".join(selected_content)
    )

    confidence = matches[0]["score"]
    needs_review = confidence < 0.20

    source_reference = "; ".join(
        f"{source['document']} "
        f"({source['section']})"
        for source in sources
    )

    query_log = ChatQueryLog(
        user_id=current_user.id,
        question=payload.question,
        answer=answer,
        source_reference=source_reference,
        confidence=confidence,
        needs_review=needs_review,
    )

    db.add(query_log)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="AI_QUERY_COMPLETED",
        entity_type="ChatQueryLog",
        entity_id=query_log.id,
        details=source_reference,
    )

    db.commit()

    return {
        "answer": answer,
        "sources": sources,
        "confidence": round(confidence, 3),
        "needs_review": needs_review,
    }


def get_query_logs(db):
    return (
        db.query(ChatQueryLog)
        .order_by(ChatQueryLog.created_at.desc())
        .all()
    )