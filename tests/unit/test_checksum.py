import hashlib

from documents.services.document import DocumentService


class TestChecksum:
    def test_checksum_is_deterministic(self) -> None:
        data = b"deterministic content for checksum"
        first = DocumentService.calculate_checksum(data)
        second = DocumentService.calculate_checksum(data)
        assert first == second

    def test_different_data_yields_different_checksum(self) -> None:
        a = DocumentService.calculate_checksum(b"data-alpha")
        b = DocumentService.calculate_checksum(b"data-beta")
        assert a != b

    def test_checksum_matches_sha256(self) -> None:
        data = b"verify sha256"
        expected = hashlib.sha256(data).hexdigest()
        assert DocumentService.calculate_checksum(data) == expected

    def test_checksum_is_64_hex_chars(self) -> None:
        result = DocumentService.calculate_checksum(b"length check")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)
