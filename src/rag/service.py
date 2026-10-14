from src.core.config import settings
from src.rag.llm import generate_answer
from src.rag.prompt import build_grounded_prompt
from src.rag.query_logging import log_chat_query
from src.rag.retrieval import retrieve_chunks


def calculate_confidence(chunks):
    if not chunks:
        return None

    similarities = [
        chunk["similarity"]
        for chunk in chunks
    ]

    return round(
        sum(similarities)
        / len(similarities),
        6,
    )


def answer_question(
    database,
    user_id,
    question,
    top_k,
    include_inactive=False,
):
    chunks = retrieve_chunks(
        database=database,
        question=question,
        top_k=top_k,
        include_inactive=(
            include_inactive
        ),
    )

    prompt = build_grounded_prompt(
        question=question,
        chunks=chunks,
    )

    answer = generate_answer(
        prompt=prompt,
        chunks=chunks,
    )

    confidence = calculate_confidence(
        chunks
    )

    sources = [
        {
            "document_id": chunk[
                "document_id"
            ],
            "document_name": chunk[
                "document_name"
            ],
            "chunk_id": chunk[
                "chunk_id"
            ],
            "chunk_index": chunk[
                "chunk_index"
            ],
            "section": chunk[
                "section"
            ],
            "similarity": chunk[
                "similarity"
            ],
        }
        for chunk in chunks
    ]

    model_name = (
        "configured-llm"
        if settings.llm_api_url
        else "retrieval-only"
    )

    logged = log_chat_query(
        database=database,
        user_id=user_id,
        question=question,
        answer=answer,
        sources=sources,
        confidence=confidence,
        model_name=model_name,
    )

    database.commit()

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "retrieval_count": len(chunks),
        "llm_used": bool(
            settings.llm_api_url
        ),
        "logged": logged,
    }
