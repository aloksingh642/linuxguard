from sklearn.ensemble import IsolationForest
import numpy as np
from app.database import engine
from app.repository import get_all_scans

def filter_scans(scans, minimum_interval=1):

    filtered = []

    previous_timestamp = None

    for scan in scans:

        if previous_timestamp is None:
            filtered.append(scan)
            previous_timestamp = scan.timestamp
            continue

        interval = (
            scan.timestamp - previous_timestamp
        ).total_seconds()

        if interval >= minimum_interval:
            filtered.append(scan)
            previous_timestamp = scan.timestamp

    return filtered

def build_feature_matrix(features):

    return np.array([
        [
            item["usage_percent"],
            item["used_size"],
            item["change_from_previous"],
            item["time_since_previous"],
            item["growth_rate"]
        ]
        for item in features
    ])


def detect_anomalies(matrix):
    if len(matrix) < 2:
        return (
            np.array([1] * len(matrix)),
            np.array([0.0] * len(matrix))
        )

    model = IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42
    )

    predictions = model.fit_predict(matrix)
    scores = model.decision_function(matrix)

    return predictions, scores

def get_scan_features():

    scans = sorted(
        get_all_scans(engine),
        key=lambda scan: scan.timestamp
    )
    scans = filter_scans(scans)
    features = []

    previous_used = None
    previous_timestamp = None

    for scan in scans:

        if previous_used is None:
            change = 0
            time_since_previous = 0
        else:
            change = scan.used_size - previous_used
            time_since_previous = (
                scan.timestamp - previous_timestamp
            ).total_seconds()

        if time_since_previous > 0:
            growth_rate = change / time_since_previous
        else:
            growth_rate = 0

        features.append({
            "usage_percent": scan.usage_percent,
            "used_size": scan.used_size,
            "change_from_previous": change,
            "time_since_previous": time_since_previous,
            "growth_rate": growth_rate
        })

        previous_used = scan.used_size
        previous_timestamp = scan.timestamp

    return features

def get_anomaly_results():

    scans = sorted(
        get_all_scans(engine),
        key=lambda scan: scan.timestamp
    )

    scans = filter_scans(scans)

    features = get_scan_features()
    matrix = build_feature_matrix(features)

    predictions, scores = detect_anomalies(matrix)

    results = []
    for index, (scan, prediction, feature) in enumerate(
        zip(scans, predictions, features)
    ):
        result = {
            "scan_id": scan.id,
            "timestamp": scan.timestamp,
            "usage_percent": scan.usage_percent,
            "used_size": scan.used_size,
            "change_from_previous": feature["change_from_previous"],
            "time_since_previous": feature["time_since_previous"],
            "growth_rate": feature["growth_rate"],
            "prediction": int(prediction),
            "anomaly": bool(prediction == -1),
            "anomaly_score": float(scores[index])
        }

        result["reason"] = explain_anomaly(result)

        results.append(result)

    return results


def explain_anomaly(result):
    if not result["anomaly"]:
        return "Normal storage behavior"

    change = result["change_from_previous"]
    growth_rate = result["growth_rate"]

    if change < 0:
        return "Unusual decrease in storage usage"

    if growth_rate > 5000:
        return "Unusually high storage growth rate"

    if change > 100 * 1024 * 1024:
        return "Large sudden increase in storage usage"

    return "Unusual storage behavior detected"
