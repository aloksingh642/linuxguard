def calculate_risk_score(category, size_gb, protected=False):

    score = 0

    # Protected directories
    if protected:
        return {
            "score": 0,
            "level": "PROTECTED"
        }

    # Size factor
    if size_gb >= 10:
        score += 40
    elif size_gb >= 5:
        score += 25
    elif size_gb >= 1:
        score += 10

    # Category factor
    if category == "Cache":
        score += 10

    elif category == "Downloads":
        score += 20

    elif category == "Personal/Other":
        score += 30

    # Convert score to risk level
    if score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": score,
        "level": level
    }
