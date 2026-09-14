from pathlib import Path

from app.scanner import (
    get_largest_files,
    get_file_type_stats,
    get_file_category_stats,
)

from app.file_classifier import get_file_category
from app.statistics import get_storage_statistics


TEST_DIR = Path(__file__).parent


def test_file_category():

    assert get_file_category(".mp4") == "Video"
    assert get_file_category(".jpg") == "Image"
    assert get_file_category(".pdf") == "Document"
    assert get_file_category(".zip") == "Archive"
    assert get_file_category(".py") == "Code"
    assert get_file_category(".unknown") == "Other"


def test_largest_files():

    files = get_largest_files(Path.home(), limit=5)

    assert isinstance(files, list)
    assert len(files) <= 5

    for file_path, size in files:
        assert file_path.is_file()
        assert size >= 0


def test_file_type_stats():

    stats = get_file_type_stats(Path.home())

    assert isinstance(stats, dict)

    for extension, data in stats.items():
        assert "count" in data
        assert "size" in data
        assert data["count"] >= 0
        assert data["size"] >= 0


def test_file_category_stats():

    stats = get_file_category_stats(Path.home())

    assert isinstance(stats, dict)

    for category, data in stats.items():
        assert "count" in data
        assert "size" in data


def test_storage_statistics():

    stats = get_storage_statistics(Path.home())

    assert stats["total_files"] >= 0
    assert stats["total_directories"] >= 0
    assert stats["total_size"] >= 0

    if stats["largest_file"] is not None:
        assert stats["largest_file_size"] >= 0
