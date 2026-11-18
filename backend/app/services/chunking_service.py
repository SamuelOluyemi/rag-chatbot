
def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    Args:
        text: Extracted document text.
        chunk_size: Maximum words per chunk.
        chunk_overlap: Number of words shared between chunks.

    Returns:
        A list of text chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size."
        )

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start += chunk_size - chunk_overlap

    return chunks
