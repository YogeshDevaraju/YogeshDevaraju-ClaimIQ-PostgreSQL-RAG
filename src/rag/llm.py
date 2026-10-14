import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.core.config import settings
from src.rag.prompt import NO_INFORMATION_MESSAGE


MAXIMUM_EXTRACT_LENGTH = 500


def make_extract(content):
    cleaned_content = " ".join(
        content.split()
    )

    if len(cleaned_content) <= MAXIMUM_EXTRACT_LENGTH:
        return cleaned_content

    return (
        cleaned_content[:MAXIMUM_EXTRACT_LENGTH].rstrip()
        + "..."
    )


def build_retrieval_only_answer(chunks):
    if not chunks:
        return NO_INFORMATION_MESSAGE

    answer_parts = [
        "Relevant ClaimIQ document extracts:"
    ]

    for position, chunk in enumerate(
        chunks,
        start=1,
    ):
        extract = make_extract(
            chunk["content"]
        )

        answer_parts.append(
            f"[Source {position}] {extract}"
        )

    return "\n\n".join(
        answer_parts
    )


def call_openai_compatible_llm(prompt):
    if not settings.llm_api_url:
        raise RuntimeError(
            "LLM_API_URL is not configured."
        )

    request_body = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer only from the "
                    "provided ClaimIQ context."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.0,
    }

    request_headers = {
        "Content-Type": "application/json",
    }

    if settings.llm_api_key:
        request_headers["Authorization"] = (
            "Bearer "
            + settings.llm_api_key
        )

    request = Request(
        settings.llm_api_url,
        data=json.dumps(
            request_body
        ).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=60,
        ) as response:
            response_data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

    except HTTPError as exc:
        error_text = exc.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"LLM HTTP error {exc.code}: "
            f"{error_text}"
        ) from exc

    except URLError as exc:
        raise RuntimeError(
            f"Unable to reach LLM: "
            f"{exc.reason}"
        ) from exc

    try:
        return (
            response_data["choices"][0]
            ["message"]["content"]
            .strip()
        )

    except (
        KeyError,
        IndexError,
        TypeError,
    ) as exc:
        raise RuntimeError(
            "Unexpected LLM response format."
        ) from exc


def generate_answer(prompt, chunks):
    if not chunks:
        return NO_INFORMATION_MESSAGE

    if not settings.llm_api_url:
        return build_retrieval_only_answer(
            chunks
        )

    return call_openai_compatible_llm(
        prompt
    )
