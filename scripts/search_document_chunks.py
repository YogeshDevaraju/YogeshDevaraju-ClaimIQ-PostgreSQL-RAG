import argparse

from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from src.db.session import SessionLocal
from src.models.document import Document
from src.models.document_chunk import DocumentChunk


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5


def search_chunks(question, top_k, include_inactive):
    if top_k < 1:
        raise SystemExit(
            "top_k must be greater than zero."
        )

    print(
        f"Loading embedding model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    question_embedding = model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    distance = (
        DocumentChunk.embedding
        .cosine_distance(
            question_embedding
        )
    )

    similarity = (
        1 - distance
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
        .order_by(distance)
        .limit(top_k)
    )

    with SessionLocal() as database:
        results = (
            database.execute(query)
            .mappings()
            .all()
        )

    print()
    print("SEMANTIC SEARCH RESULTS")
    print("=" * 100)
    print(f"Question         : {question}")
    print(f"Requested top-k  : {top_k}")
    print(
        "Include inactive : "
        f"{'YES' if include_inactive else 'NO'}"
    )
    print(
        f"Results returned : {len(results)}"
    )

    if not results:
        print()
        print(
            "No eligible embedded chunks found."
        )
        return

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print()
        print("-" * 100)
        print(f"Rank          : {rank}")
        print(
            "Similarity    : "
            f"{float(result['similarity']):.6f}"
        )
        print(
            f"Document ID   : "
            f"{result['document_id']}"
        )
        print(
            f"Document Name : "
            f"{result['document_name']}"
        )
        print(
            f"Approved      : "
            f"{result['is_approved']}"
        )
        print(
            f"Chunk ID      : "
            f"{result['chunk_id']}"
        )
        print(
            f"Chunk Index   : "
            f"{result['chunk_index']}"
        )
        print(
            f"Section       : "
            f"{result['section']}"
        )
        print()
        print("SOURCE CONTENT:")
        print(result["content"])


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Search ClaimIQ document chunks "
            "using PostgreSQL pgvector."
        )
    )

    parser.add_argument(
        "question",
        help="Question or search text.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help="Number of results to return.",
    )

    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help=(
            "Include unapproved documents."
        ),
    )

    arguments = parser.parse_args()

    search_chunks(
        question=arguments.question,
        top_k=arguments.top_k,
        include_inactive=(
            arguments.include_inactive
        ),
    )


if __name__ == "__main__":
    main()
