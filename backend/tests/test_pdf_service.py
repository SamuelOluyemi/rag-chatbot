import pymupdf
import pytest

from app.services.pdf_service import extract_text_from_pdf


def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72, 72), "This is a test PDF document.")
        pdf.save(pdf_path)

    extracted_text = extract_text_from_pdf(pdf_path)

    assert "This is a test PDF document." in extracted_text


def test_missing_pdf_raises_error(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(pdf_path)


def test_pdf_without_extractable_text_raises_error(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    with pymupdf.open() as pdf:
        pdf.new_page()
        pdf.save(pdf_path)

    with pytest.raises(ValueError, match="No extractable text"):
        extract_text_from_pdf(pdf_path)
        