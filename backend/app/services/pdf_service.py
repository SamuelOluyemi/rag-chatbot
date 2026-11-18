
from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract text from all pages of a PDF document.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text from the PDF.

    Raises:
        ValueError: If the PDF contains no extractable text.
        FileNotFoundError: If the PDF file does not exist.
    """

    pdf_path = Path(file_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    extracted_pages = []

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            page_text = page.get_text().strip()

            if page_text:
                extracted_pages.append(page_text)

    full_text = "\n\n".join(extracted_pages)

    if not full_text:
        raise ValueError(
            "No extractable text found in the PDF."
        )

    return full_text
