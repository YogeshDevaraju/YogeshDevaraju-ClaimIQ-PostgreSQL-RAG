from sentence_transformers import SentenceTransformer
from sqlalchemy import select, text

from src.db.session import SessionLocal
from src.models.document_chunk import DocumentChunk


MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)

EXPECTED_DIMENSIONS = 384

TRIGGER_NAME = (
    "document_chunks_entity_history"
)


def trigger_exists(database):
    query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM pg_trigger
            WHERE tgname = :trigger_name
              AND NOT tgisinternal
        )
        """
    )

    return database.execute(
        query,
        {
            "trigger_name": TRIGGER_NAME,
        },
    ).scalar_one()


def main():
    print(
        f"Loading embedding model: "
        f"{MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    with SessionLocal() as database:
        chunks = (
            database.execute(
                select(DocumentChunk)
                .where(
                    DocumentChunk.embedding
                    .is_(None)
                )
                .order_by(
                    DocumentChunk.id
                )
            )
            .scalars()
            .all()
        )

        print(
            f"Chunks requiring embeddings: "
            f"{len(chunks)}"
        )

        if not chunks:
            print(
                "All document chunks already "
                "have embeddings."
            )
            return

        contents = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = model.encode(
            contents,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Embedding count does not "
                "match the chunk count."
            )

        history_trigger_exists = (
            trigger_exists(database)
        )

        try:
            if history_trigger_exists:
                database.execute(
                    text(
                        "ALTER TABLE "
                        "document_chunks "
                        "DISABLE TRIGGER "
                        "document_chunks_entity_history"
                    )
                )

                print(
                    "Temporarily disabled the "
                    "document chunk history trigger."
                )

            for chunk, embedding in zip(
                chunks,
                embeddings,
            ):
                if len(embedding) != (
                    EXPECTED_DIMENSIONS
                ):
                    raise RuntimeError(
                        f"Chunk {chunk.id} produced "
                        f"{len(embedding)} dimensions; "
                        f"expected "
                        f"{EXPECTED_DIMENSIONS}."
                    )

                chunk.embedding = (
                    embedding.tolist()
                )

                print(
                    f"Prepared chunk ID "
                    f"{chunk.id}, index "
                    f"{chunk.chunk_index}"
                )

            database.flush()

            if history_trigger_exists:
                database.execute(
                    text(
                        "ALTER TABLE "
                        "document_chunks "
                        "ENABLE TRIGGER "
                        "document_chunks_entity_history"
                    )
                )

                print(
                    "Re-enabled the document "
                    "chunk history trigger."
                )

            database.commit()

        except Exception:
            database.rollback()
            raise

        print()
        print(
            f"Successfully stored "
            f"{len(chunks)} embeddings."
        )


if __name__ == "__main__":
    main()
