from functools import lru_cache

from sentence_transformers import SentenceTransformer

from src.core.config import settings


EXPECTED_DIMENSIONS = 384


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(
        settings.embedding_model
    )


def embed_text(text):
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError(
            "Text cannot be empty."
        )

    model = get_embedding_model()

    embedding = model.encode(
        cleaned_text,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    if len(embedding) != EXPECTED_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EXPECTED_DIMENSIONS} dimensions, "
            f"received {len(embedding)}."
        )

    return embedding.tolist()


def embed_texts(texts):
    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    result = []

    for embedding in embeddings:
        if len(embedding) != EXPECTED_DIMENSIONS:
            raise RuntimeError(
                f"Expected {EXPECTED_DIMENSIONS} dimensions, "
                f"received {len(embedding)}."
            )

        result.append(
            embedding.tolist()
        )

    return result
