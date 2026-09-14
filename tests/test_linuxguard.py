# "I created unit tests using pytest for directory classification,
#  protected-directory handling, risk scoring, and cleanup recommendations."


from app.analyzer import analyze_directory
from app.risk_engine import calculate_risk_score
from app.recommender import get_recommendation


def test_protected_directory():

    result = analyze_directory(".ssh")

    assert result["category"] == "System/Security"
    assert result["risk"] == "PROTECTED"


def test_cache_directory():

    result = analyze_directory(".cache")

    assert result["category"] == "Cache"
    assert result["risk"] == "SAFE_TO_REVIEW"


def test_download_directory():

    result = analyze_directory("Downloads")

    assert result["category"] == "Downloads"
    assert result["risk"] == "REVIEW"


def test_large_personal_directory():

    result = calculate_risk_score(
        "Personal/Other",
        15,
        protected=False
    )

    assert result["score"] == 70
    assert result["level"] == "HIGH"


def test_protected_risk():

    result = calculate_risk_score(
        "System/Security",
        20,
        protected=True
    )

    assert result["score"] == 0
    assert result["level"] == "PROTECTED"


def test_cache_recommendation():

    result = get_recommendation(
        ".cache",
        "Cache",
        "SAFE_TO_REVIEW",
        5
    )

    assert "cleanup" in result.lower()


def test_protected_recommendation():

    result = get_recommendation(
        ".ssh",
        "System/Security",
        "PROTECTED",
        2
    )

    assert "delete" in result.lower()
