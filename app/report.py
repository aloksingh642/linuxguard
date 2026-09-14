from pathlib import Path

from app.scanner import (
    get_directories,
    get_directory_size,
    get_file_category_stats,
    get_largest_files,
)

from app.statistics import get_storage_statistics
from app.analyzer import analyze_directory
from app.risk_engine import calculate_risk_score
from app.recommender import get_recommendation


def format_gb(size):
    return size / (1024 ** 3)


def generate_report(path):

    path = Path(path)

    # Overall statistics
    statistics = get_storage_statistics(path)

    # Directory analysis
    directories = get_directories(path)

    directory_data = []

    for directory in directories:

        size = get_directory_size(directory)
        size_gb = format_gb(size)

        analysis = analyze_directory(directory.name)

        risk = calculate_risk_score(
            analysis["category"],
            size_gb,
            protected=(analysis["risk"] == "PROTECTED")
        )

        recommendation = get_recommendation(
            directory.name,
            analysis["category"],
            analysis["risk"],
            size_gb
        )

        directory_data.append({
            "name": directory.name,
            "size": size,
            "category": analysis["category"],
            "risk": risk["level"],
            "risk_score": risk["score"],
            "recommendation": recommendation,
        })

    directory_data.sort(
        key=lambda item: item["size"],
        reverse=True
    )

    # File categories
    category_stats = get_file_category_stats(path)

    # Largest files
    largest_files = get_largest_files(path, limit=10)

    return {
        "statistics": statistics,
        "directories": directory_data,
        "categories": category_stats,
        "largest_files": largest_files,
    }
