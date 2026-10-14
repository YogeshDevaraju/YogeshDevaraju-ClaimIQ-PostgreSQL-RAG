from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_rag_empty_question_is_rejected():
    response = client.post(
        "/chat/query",
        json={
            "question": "",
            "top_k": 3,
            "include_inactive": False,
            "user_id": 1,
        },
    )

    assert response.status_code == 422


def test_rag_invalid_top_k_is_rejected():
    response = client.post(
        "/chat/query",
        json={
            "question": (
                "What is covered under "
                "motor insurance?"
            ),
            "top_k": 21,
            "include_inactive": False,
            "user_id": 1,
        },
    )

    assert response.status_code == 422


def test_rag_query_succeeds():
    response = client.post(
        "/chat/query",
        json={
            "question": (
                "What is covered under "
                "comprehensive motor insurance?"
            ),
            "top_k": 3,
            "include_inactive": False,
            "user_id": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
    assert "retrieval_count" in data
    assert "llm_used" in data
    assert "logged" in data

    assert data["retrieval_count"] <= 3
    assert data["llm_used"] is False
    assert data["logged"] is True

    for source in data["sources"]:
        assert "document_id" in source
        assert "document_name" in source
        assert "chunk_id" in source
        assert "chunk_index" in source
        assert "similarity" in source


