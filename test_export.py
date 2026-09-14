from pathlib import Path

from app.report import generate_report
from app.exporter import export_json


report = generate_report(Path.home())

filename = export_json(report)

print(f"Report exported successfully: {filename}")
