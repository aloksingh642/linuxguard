from app.anomaly import (
    get_anomaly_results,
    explain_anomaly,
)


def test_anomaly_results_structure():
    results = get_anomaly_results()

    assert len(results) > 0

    required_keys = {
        "scan_id",
        "timestamp",
        "usage_percent",
        "used_size",
        "change_from_previous",
        "time_since_previous",
        "growth_rate",
        "prediction",
        "anomaly",
        "anomaly_score",
        "reason",
    }

    for result in results:
        assert required_keys.issubset(result.keys())


def test_prediction_values():
    results = get_anomaly_results()

    for result in results:
        assert result["prediction"] in {-1, 1}
        assert isinstance(result["anomaly"], bool)


def test_anomaly_score_is_numeric():
    results = get_anomaly_results()

    for result in results:
        assert isinstance(result["anomaly_score"], float)


def test_explanation_for_normal_scan():
    result = {
        "anomaly": False,
        "change_from_previous": 0,
        "growth_rate": 0,
    }

    assert explain_anomaly(result) == "Normal storage behavior"


def test_explanation_for_storage_decrease():
    result = {
        "anomaly": True,
        "change_from_previous": -500000000,
        "growth_rate": -5000,
    }

    assert (
        explain_anomaly(result)
        == "Unusual decrease in storage usage"
    )


def test_explanation_for_high_growth():
    result = {
        "anomaly": True,
        "change_from_previous": 5000000,
        "growth_rate": 6000,
    }

    assert (
        explain_anomaly(result)
        == "Unusually high storage growth rate"
    )
