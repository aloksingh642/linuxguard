import json


def export_json(data, filename="linuxguard_report.json"):

    with open(filename, "w") as file:
        json.dump(data, file, indent=4, default=str)

    return filename
