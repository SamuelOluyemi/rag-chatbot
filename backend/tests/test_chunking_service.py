import pytest

from app.services.chunking_service import split_text_into_chunks


def test_split_text_into_chunks():
    text = "one two three four five six"

    chunks = split_text_into_chunks(
        text,
        chunk_size=3,
        chunk_overlap=1,
    )

    assert chunks == [
        "one two three",
        "three four five",
        "five six",
    ]


def test_empty_text_returns_empty_list():
    assert split_text_into_chunks("") == []


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        split_text_into_chunks("some text", chunk_size=0)


def test_invalid_chunk_overlap_raises_error():
    with pytest.raises(ValueError):
        split_text_into_chunks(
            "some text",
            chunk_size=5,
            chunk_overlap=5,
        )
        