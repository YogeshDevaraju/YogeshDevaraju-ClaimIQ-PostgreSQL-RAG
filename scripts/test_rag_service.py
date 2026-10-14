import json

from src.db.session import SessionLocal
from src.rag.service import answer_question


QUESTION = (
    "What is covered under "
    "comprehensive motor insurance?"
)

TEST_USER_ID = 1


def main():
    with SessionLocal() as database:
        result = answer_question(
            database=database,
            user_id=TEST_USER_ID,
            question=QUESTION,
            top_k=3,
            include_inactive=False,
        )

    print()
    print("RAG SERVICE RESULT")
    print("=" * 100)

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
