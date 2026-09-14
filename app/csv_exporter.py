import csv


def export_directories_csv(
    directories,
    filename="linuxguard_directories.csv"
):

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Name",
            "Size_GB",
            "Category",
            "Risk",
            "Risk_Score",
            "Recommendation"
        ])

        for item in directories:

            writer.writerow([
                item["name"],
                round(item["size"] / (1024 ** 3), 2),
                item["category"],
                item["risk"],
                item["risk_score"],
                item["recommendation"]
            ])

    return filename
