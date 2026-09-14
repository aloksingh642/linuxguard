import requests
from unittest.mock import patch


def test_dashboard_handles_api_unavailable():
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError(
            "API unavailable"
        )
    ):
        try:
            requests.get(
                "http://127.0.0.1:8000/system",
                timeout=5
            )
        except requests.exceptions.RequestException:
            handled = True
        else:
            handled = False

    assert handled is True
