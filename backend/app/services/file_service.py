
import hashlib
from pathlib import Path


def calculate_file_hash(file_path: str | Path) -> str:
    """
    Calculate the SHA-256 hash of a file.

    Reads the file in chunks to avoid loading the entire
    file into memory.

    Args:
        file_path: Path to the file.

    Returns:
        A 64-character hexadecimal SHA-256 hash.
    """

    sha256 = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()
