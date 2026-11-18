
from pathlib import Path

from app.services.file_service import calculate_file_hash


def test_file_hash():
    file_path = Path("backend/uploads/LLM Test Doc.pdf")

    file_hash = calculate_file_hash(file_path)

    print("File:", file_path.name)
    print("SHA-256:", file_hash)
    print("Hash length:", len(file_hash))

    assert len(file_hash) == 64

    print("\nFile hashing test completed!")


if __name__ == "__main__":
    test_file_hash()

