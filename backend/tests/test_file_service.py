from app.services.file_service import calculate_file_hash


def test_identical_files_produce_same_hash(tmp_path):
    file_one = tmp_path / "document_one.pdf"
    file_two = tmp_path / "document_two.pdf"

    file_one.write_bytes(b"Sample PDF content")
    file_two.write_bytes(b"Sample PDF content")

    assert calculate_file_hash(file_one) == calculate_file_hash(file_two)


def test_different_files_produce_different_hashes(tmp_path):
    file_one = tmp_path / "document_one.pdf"
    file_two = tmp_path / "document_two.pdf"

    file_one.write_bytes(b"First document")
    file_two.write_bytes(b"Second document")

    assert calculate_file_hash(file_one) != calculate_file_hash(file_two)


def test_hash_is_64_characters(tmp_path):
    file_path = tmp_path / "document.pdf"
    file_path.write_bytes(b"Sample PDF content")

    file_hash = calculate_file_hash(file_path)

    assert len(file_hash) == 64
    