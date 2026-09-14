from pathlib import Path

from app.cleanup import (
    is_protected,
    is_cleanup_allowed,
)


def test_ssh_is_protected():
    path = Path.home() / ".ssh" / "id_rsa"

    assert is_protected(path) is True


def test_gnupg_is_protected():
    path = Path.home() / ".gnupg" / "example"

    assert is_protected(path) is True


def test_config_is_protected():
    path = Path.home() / ".config" / "example"

    assert is_protected(path) is True


def test_cache_is_allowed(tmp_path):
    cache_dir = tmp_path / "user" / ".cache"
    cache_dir.mkdir(parents=True)

    test_file = cache_dir / "example.tmp"
    test_file.write_text("LinuxGuard test")

    with __import__("unittest").mock.patch(
        "app.cleanup.SCAN_ROOT",
        tmp_path,
    ):
        assert is_cleanup_allowed(
            test_file,
            tmp_path,
        ) is True


def test_downloads_is_allowed(tmp_path):
    downloads_dir = tmp_path / "user" / "Downloads"
    downloads_dir.mkdir(parents=True)

    test_file = downloads_dir / "example.zip"
    test_file.write_text("LinuxGuard test")

    with __import__("unittest").mock.patch(
        "app.cleanup.SCAN_ROOT",
        tmp_path,
    ):
        assert is_cleanup_allowed(
            test_file,
            tmp_path,
        ) is True


def test_documents_are_not_allowed(tmp_path):
    documents_dir = tmp_path / "user" / "Documents"
    documents_dir.mkdir(parents=True)

    test_file = documents_dir / "example.pdf"
    test_file.write_text("LinuxGuard test")

    with __import__("unittest").mock.patch(
        "app.cleanup.SCAN_ROOT",
        tmp_path,
    ):
        assert is_cleanup_allowed(
            test_file,
            tmp_path,
        ) is False
