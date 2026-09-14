from unittest.mock import patch

from app.cleanup import cleanup_files


def test_dry_run_does_not_delete(tmp_path):
    test_file = tmp_path / "test.tmp"

    test_file.write_text("LinuxGuard test")

    cleanup_files(
        [test_file],
        dry_run=True
    )

    assert test_file.exists()


def test_permission_error_during_cleanup(tmp_path):
    test_file = tmp_path / "permission_test.tmp"

    test_file.write_text("LinuxGuard permission test")

    with patch(
        "app.cleanup.Path.unlink",
        side_effect=PermissionError("Permission denied")
    ):
        deleted = cleanup_files(
            [test_file],
            dry_run=False,
            confirmed=True
        )

    assert deleted == []
