NO_INFORMATION_MESSAGE = (
    "I could not find enough information "
    "in the available ClaimIQ documents."
)


def build_grounded_prompt(
    question,
    chunks,
):
    context_sections = []

    for position, chunk in enumerate(
        chunks,
        start=1,
    ):
        context_sections.append(
            "\n".join(
                [
                    f"[Source {position}]",
                    (
                        "Document ID: "
                        f"{chunk['document_id']}"
                    ),
                    (
                        "Document Name: "
                        f"{chunk['document_name']}"
                    ),
                    (
                        "Chunk ID: "
                        f"{chunk['chunk_id']}"
                    ),
                    (
                        "Chunk Index: "
                        f"{chunk['chunk_index']}"
                    ),
                    (
                        "Section: "
                        f"{chunk['section']}"
                    ),
                    "Content:",
                    chunk["content"],
                ]
            )
        )

    context_text = "\n\n".join(
        context_sections
    )

    return f"""
You are the ClaimIQ insurance assistant.

Answer the question using only the supplied context.

Rules:
1. Do not invent policy terms, coverage, exclusions, dates, amounts, or claim requirements.
2. If the context does not contain enough information, respond exactly with:
"{NO_INFORMATION_MESSAGE}"
3. Keep the answer concise and factual.
4. Refer to supporting sources as [Source 1], [Source 2], and so on.
5. Do not mention information that is not in the context.

Question:
{question}

Context:
{context_text}
""".strip()
