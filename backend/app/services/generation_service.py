
import httpx
import os

# OLLAMA_API_URL = "http://localhost:11434/api/generate"
# Change the model name to the one you want to use. For example, "llama3.1:8b" or "llama3.1:13b".
# OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL") or "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL") or "llama3.2:3b"


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
        "options": {
            "num_predict": 256,
            "temperature": 0.2,
        },
        "keep_alive": "30m",
    }

    try:
        response = httpx.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=600.0,
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
