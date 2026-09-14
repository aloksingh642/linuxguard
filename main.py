from pathlib import Path

from app.scanner import get_directories, get_directory_size
from app.analyzer import analyze_directory
from app.recommender import get_recommendation
from app.risk_engine import calculate_risk_score

def format_gb(bytes_value):
    return bytes_value / (1024 ** 3)


def main():

    home = Path.home()

    directories = get_directories(home)

    directory_sizes = []

    for directory in directories:

        size = get_directory_size(directory)

        analysis = analyze_directory(directory.name)

        size_gb = format_gb(size)

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

        directory_sizes.append({
            "name": directory.name,
            "size": size,
            "category": analysis["category"],
            "risk": analysis["risk"],
            "risk_score": risk["score"],
            "risk_level": risk["level"],
            "recommendation": recommendation,
        })

    # Sort by size
    directory_sizes.sort(
        key=lambda item: item["size"],
        reverse=True
    )

    print("LinuxGuard Storage Report")
    print("=" * 75)

    for index, item in enumerate(directory_sizes[:10], start=1):

        print(
                f"\n{index}. {item['name']}"
         )

        print(
            f"   Size:           "
            f"{format_gb(item['size']):.2f} GB"
        )

        print(
            f"   Category:       "
            f"{item['category']}"
        )

        print(
            f"   Risk:           "
            f"{item['risk']}"
        )

        print(
             f"   Risk Score:     "
             f"{item['risk_score']}"
            )

        print(
            f"   Risk Level:     "
            f"{item['risk_level']}"
        )

        print(
            f"   Recommendation: "
            f"{item['recommendation']}"
        )


if __name__ == "__main__":
    main()