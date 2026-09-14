import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)

HOME = Path(os.environ.get("HOME", "/home/testuser"))
DOWNLOADS = HOME / "Downloads"
SSH = HOME / ".ssh"
DOCUMENTS = HOME / "Documents"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "LinuxGuard API is running"
    }


def test_system_endpoint():
    response = client.get("/system")

    assert response.status_code == 200

    data = response.json()

    assert "disk_usage_percent" in data
    assert "status" in data
    assert "total" in data
    assert "used" in data
    assert "free" in data


def test_anomalies_endpoint():
    response = client.get("/anomalies")

    assert response.status_code == 200

    data = response.json()

    assert "total_scans" in data
    assert "anomaly_count" in data
    assert "results" in data

    assert isinstance(data["results"], list)


def test_cleanup_requires_confirmation():
    test_file = DOWNLOADS / "linuxguard_api_test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("LinuxGuard API test")

    try:
        response = client.post(
            "/cleanup",
            json={
                "file_path": str(test_file),
                "confirmed": False
            }
        )

        assert response.status_code == 400
        assert test_file.exists()

    finally:
        if test_file.exists():
            test_file.unlink()


def test_cleanup_protected_file():
    test_file = SSH / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("protected test")

    try:
        response = client.post(
            "/cleanup",
            json={
                "file_path": str(test_file),
                "confirmed": True
            }
        )

        assert response.status_code == 403

    finally:
        if test_file.exists():
            test_file.unlink()


def test_cleanup_missing_file():
    test_file = DOWNLOADS / "file_that_does_not_exist.txt"

    if test_file.exists():
        test_file.unlink()

    response = client.post(
        "/cleanup",
        json={
            "file_path": str(test_file),
            "confirmed": True
        }
    )

    assert response.status_code == 404


def test_cleanup_directory_path():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    response = client.post(
        "/cleanup",
        json={
            "file_path": str(DOWNLOADS),
            "confirmed": True
        }
    )

    assert response.status_code == 400


def test_cleanup_non_allowed_path():
    test_file = DOCUMENTS / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("non allowed test")

    try:
        response = client.post(
            "/cleanup",
            json={
                "file_path": str(test_file),
                "confirmed": True
            }
        )

        assert response.status_code == 403

    finally:
        if test_file.exists():
            test_file.unlink()


def test_cleanup_invalid_request_body():
    response = client.post(
        "/cleanup",
        json={
            "confirmed": True
        }
    )

    assert response.status_code == 422


def test_scan_database_failure():
    with patch(
        "app.api.save_scan",
        side_effect=Exception("Database unavailable")
    ):
        response = client.post("/scan")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to save scan"
    }


def test_scans_database_failure():
    with patch(
        "app.api.get_all_scans",
        side_effect=Exception("Database unavailable")
    ):
        response = client.get("/scans")

    assert response.status_code == 500


def test_cleanup_invalid_file_path_type():
    response = client.post(
        "/cleanup",
        json={
            "file_path": 12345,
            "confirmed": True
        }
    )

    assert response.status_code == 422


def test_cleanup_invalid_confirmed_type():
    response = client.post(
        "/cleanup",
        json={
            "file_path": str(DOWNLOADS / "test.txt"),
            "confirmed": "definitely-not-a-boolean"
        }
    )

    assert response.status_code == 422


def test_cleanup_empty_file_path():
    response = client.post(
        "/cleanup",
        json={
            "file_path": "",
            "confirmed": True
        }
    )

    assert response.status_code == 422
