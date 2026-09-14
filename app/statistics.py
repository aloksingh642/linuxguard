from pathlib import Path


def get_storage_statistics(path):

    path = Path(path)

    total_files = 0
    total_directories = 0
    total_size = 0

    largest_file = None
    largest_file_size = 0

    largest_directory = None
    largest_directory_size = 0

    for item in path.rglob("*"):

        try:

            if item.is_file():

                total_files += 1

                size = item.stat().st_size
                total_size += size

                if size > largest_file_size:
                    largest_file = item
                    largest_file_size = size

            elif item.is_dir():

                total_directories += 1

        except (PermissionError, OSError):
            pass

    return {
        "total_files": total_files,
        "total_directories": total_directories,
        "total_size": total_size,
        "largest_file": largest_file,
        "largest_file_size": largest_file_size,
        "largest_directory": largest_directory,
        "largest_directory_size": largest_directory_size,
    }
