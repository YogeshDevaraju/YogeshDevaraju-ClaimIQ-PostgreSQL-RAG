import argparse
from pathlib import Path

from sqlalchemy import inspect, text

from src.db.session import engine


PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)


def require_tables(connection):
    database_inspector = inspect(
        connection
    )

    available_tables = set(
        database_inspector.get_table_names()
    )

    required_tables = {
        "documents",
        "document_chunks",
    }

    missing_tables = sorted(
        required_tables
        - available_tables
    )

    if missing_tables:
        raise SystemExit(
            "Missing PostgreSQL tables: "
            + ", ".join(missing_tables)
            + ". Run: python -m "
            "src.db.init_db"
        )


def show_chunk_range(
    document_id,
    start_index,
    end_index,
):
    if engine.dialect.name != "postgresql":
        raise SystemExit(
            "This script requires PostgreSQL. "
            f"Current database dialect: "
            f"{engine.dialect.name}"
        )

    if start_index > end_index:
        raise SystemExit(
            "StartIndex cannot be greater "
            "than EndIndex."
        )

    with engine.connect() as connection:
        require_tables(
            connection
        )

        document_query = text(
            """
            SELECT
                id,
                name,
                file_path,
                is_approved,
                uploaded_by,
                uploaded_at
            FROM documents
            WHERE id = :document_id
            """
        )

        document = (
            connection.execute(
                document_query,
                {
                    "document_id": (
                        document_id
                    )
                },
            )
            .mappings()
            .first()
        )

        if document is None:
            raise SystemExit(
                f"Document ID {document_id} "
                "was not found."
            )

        count_query = text(
            """
            SELECT COUNT(*)
            FROM document_chunks*            WHERE document_id = :d*cument_id
            """
        *

        total_chunks = (
       *    connection.execute(
          *     count_query,
                *
                    "document_id"* (
                        documen*_id
                    )
        *       },
            )
          * .scalar_one()
        )

        *hunks_query = text(
            ""*
            SELECT
              * id,
                document_id,
*               chunk_index,
      *         section,
                *ontent,
                char_lengt*(content)
                    AS c*aracter_count
            FROM doc*ment_chunks
            WHERE docu*ent_id = :document_id
            * AND chunk_index
                 *BETWEEN :start_index
             *    AND :end_index
            ORD*R BY chunk_index
            """
 *      )

        chunks = (
      *     connection.execute(
         *      chunks_query,
              * {
                    "document_i*": (
                        docum*nt_id
                    ),
     *              "start_index": (
   *                    start_index
  *                 ),
              *     "end_index": (
              *         end_index
               *    ),
                },
        *   )
            .mappings()
     *      .all()
        )

    stored*path = (
        document["file_path"]
        or ""
    )

    physi*al_path = Path(
        stored_pat*
    )

    if not physical_path.i*_absolute():
        physical_path*= (
            PROJECT_ROOT
     *      / physical_path
        )

 *  if physical_path.exists():
     *  file_size = (
            physic*l_path.stat().st_size
        )

 *      physical_status = "FOUND"

 *  else:
        file_size = 0
    *   physical_status = "NOT FOUND"

*   if bool(document["is_approved"\]):
        status = "ACTIVE"
    e*se:
        status = "INACTIVE"

 *  print()
    print("DOCUMENT DETA*LS")
    print("=" * 100)

    pri*t(
        f"Database          : "*        f"{engine.url.database}"
 *  )

    print(
        f"Server  *         : "
        f"{engine.url*host}:"
        f"{engine.url.port*"
    )

    print(
        f"Docu*ent ID       : "
        f"{docume*t['id']}"
    )

    print(
      * f"Document Name     : "
        f*{document['name']}"
    )

    pri*t(
        f"File Path         : "*        f"{stored_path}"
    )

  * print(
        f"Physical File   * : "
        f"{physical_status}"
*   )

    print(
        f"File Si*e         : "
        f"{file_size* bytes"
    )

    print(
        *"Status            : "
        f"{*tatus}"
    )

    print(
        *"Uploaded By       : "
        f"{*ocument['uploaded_by']}"
    )

  * print(
        f"Uploaded At     * : "
        f"{document['uploaded_at']}"
    )

    print(
        f*Total Chunks      : "
        f"{t*tal_chunks}"
    )

    print(
   *    f"Requested Range   : "
      * f"{start_index} to {end_index}"
 *  )

    print(
        f"Chunks R*turned   : "
        f"{len(chunks*}"
    )

    if not chunks:
     *  print()

        print(
        *   "No chunks were found in the "
*           "requested range."
    *   )

        return

    for chun* in chunks:
        print()
      * print("=" * 100)

        print(
*           f"Chunk ID          : "*            f"{chunk['id']}"
     *  )

        print(
            f"*ocument ID       : "
            f*{chunk['document_id']}"
        )

        print(
            f"Chunk Index       : "
            f"{chunk['chunk_index']}"
        )

        print(
            f"Section           : "
            f"{chunk['section']}"
        )

        print(
            f"Chunk Size        : "
            f"{chunk['character_count']} "
            f"characters"
        )

        print("-" * 100)

        print(
            chunk["content"]
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Show PostgreSQL document "
            "details and a selected range "
            "of document chunks."
        )
    )

    parser.add_argument(
        "document_id",
        type=int,
    )

    parser.add_argument(
        "start_index",
        type=int,
    )

    parser.add_argument(
        "end_index",
        type=int,
    )

    arguments = parser.parse_args()

    show_chunk_range(
        document_id=(
            arguments.document_id
        ),
        start_index=(
            arguments.start_index
        ),
        end_index=(
            arguments.end_index
        ),
    )


if __name__ == "__main__":
    main()