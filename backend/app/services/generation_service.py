
import httpx


OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"


def generate_answer(
    query: str,
    context: list[str],
) -> str:
    """
    Generate an answer using Ollama and retrieved document context.

    Args:
        query: The user's question.
        context: Relevant text chunks retrieved from documents.

    Returns:
        The generated answer.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if not context:
        return "I couldn't find relevant information in your documents."

    # Combine retrieved chunks into a single context.
    document_context = "\n\n".join(context)

    # Construct the prompt for the local LLM.
    prompt = f"""
You are a helpful assistant that answers questions using
the provided document context.

Instructions:
- Answer using only the information in the context.
- Do not invent facts or introduce unsupported information.
- If the context does not contain the answer, say so clearly.
- Provide a clear and concise response.

Document context:
{document_context}

User question:
{query}

Answer:
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = httpx.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=120.0,
        )

        response.raise_for_status()

        result = response.json()

        return result["response"].strip()

    except httpx.TimeoutException as exc:
        raise RuntimeError(
            "Ollama request timed out."
        ) from exc

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Failed to communicate with Ollama: {exc}"
        ) from exc
