from pathlib import Path
from app.file_classifier import get_file_category

def get_directories(path):
    path = Path(path)

    directories = []

    for item in path.iterdir():
        if item.is_dir():
            directories.append(item)

    return directories
def get_directory_size(path):
    total_size = 0

    for item in Path(path).rglob("*"):
        if item.is_file():
            try:
                total_size += item.stat().st_size
            except PermissionError:
                pass

    return total_size

def get_largest_files(path, limit=10):

    path = Path(path)

    files = []

    for item in path.rglob("*"):

        if item.is_file():

            try:
                size = item.stat().st_size
                files.append((item, size))

            except (PermissionError, OSError):
                pass

    files.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return files[:limit]
def get_file_type_stats(path):

    path = Path(path)

    stats = {}

    for item in path.rglob("*"):

        if not item.is_file():
            continue

        try:
            size = item.stat().st_size

            extension = item.suffix.lower()

            if not extension:
                file_type = "No Extension"
            else:
                file_type = extension

            if file_type not in stats:
                stats[file_type] = {
                    "count": 0,
                    "size": 0
                }

            stats[file_type]["count"] += 1
            stats[file_type]["size"] += size

        except (PermissionError, OSError):
            pass

    return stats
def get_file_category_stats(path):

    path = Path(path)

    stats = {}

    for item in path.rglob("*"):

        if not item.is_file():
            continue

        try:
            size = item.stat().st_size

            extension = item.suffix.lower()

            category = get_file_category(extension)

            if category not in stats:
                stats[category] = {
                    "count": 0,
                    "size": 0
                }

            stats[category]["count"] += 1
            stats[category]["size"] += size

        except (PermissionError, OSError):
            pass

    return stats
