from pathlib import Path

from app.report import generate_report
from app.csv_exporter import export_directories_csv


report = generate_report(Path.home())

filename = export_directories_csv(
    report["directories"]
)

print(f"CSV exported successfully: {filename}")
