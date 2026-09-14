from app.cleanup import cleanup_files


def test_cleanup_database(tmp_path, monkeypatch):
    scan_root = tmp_path / "scan"
    cleanup_root = tmp_path / "cleanup"

    source_cache = scan_root / "testuser" / ".cache"
    writable_cache = cleanup_root / "testuser" / ".cache"

    source_cache.mkdir(parents=True)
    writable_cache.mkdir(parents=True)

    source_file = source_cache / "test.tmp"
    cleanup_file = writable_cache / "test.tmp"

    source_file.write_text("LinuxGuard database test")
    cleanup_file.write_text("LinuxGuard database test")

    monkeypatch.setattr(
        "app.cleanup.SCAN_ROOT",
        scan_root,
    )
    monkeypatch.setattr(
        "app.cleanup.CLEANUP_ROOT",
        cleanup_root,
    )

    deleted = cleanup_files(
        [source_file],
        dry_run=False,
        confirmed=True,
    )

    assert deleted == [source_file]
    assert source_file.exists()
    assert cleanup_file.exists() is False
