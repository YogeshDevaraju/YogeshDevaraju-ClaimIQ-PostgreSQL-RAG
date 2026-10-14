import pytest

from src.db.session import SessionLocal
from src.rag.embeddings import embed_text
from src.rag.retrieval import retrieve_chunks


def test_embedding_dimensions():
    embedding = embed_text(
        "ClaimIQ embedding test"
    )

    assert len(embedding) == 384


def test_retrieval_top_k():
    with SessionLocal() as database:
        results = retrieve_chunks(
            database=database,
            question=(
                "What is covered under "
                "motor insurance?"
            ),
            top_k=3,
            include_inactive=False,
        )

    assert len(results) <= 3

    for result in results:
        assert result["is_approved"] is True
        assert "document_id" in result
        assert "document_name" in result
        assert "chunk_id" in result
        assert "chunk_index" in result
        assert "similarity" in result


def test_top_k_zero_is_rejected():
    with SessionLocal() as database:
        with pytest.raises(ValueError):
            retrieve_chunks(
                database=database,
                question="Motor insurance",
                top_k=0,
                include_inactive=False,
            )


def test_top_k_above_limit_is_rejected():
    with SessionLocal() as database:
        with pytest.raises(ValueError):
            retrieve_chunks(
                database=database,
                question="Motor insurance",
                top_k=21,
                include_inactive=False,
            )
