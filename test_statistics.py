from pathlib import Path

from app.statistics import get_storage_statistics


stats = get_storage_statistics(Path.home())


print("LinuxGuard Storage Statistics")
print("=" * 50)

print(f"Total Files:       {stats['total_files']}")
print(f"Total Directories: {stats['total_directories']}")
print(
    f"Total Size:        "
    f"{stats['total_size'] / (1024 ** 3):.2f} GB"
)

if stats["largest_file"]:

    print(
        f"Largest File:     "
        f"{stats['largest_file']}"
    )

    print(
        f"Largest File Size:"
        f" {stats['largest_file_size'] / (1024 ** 3):.2f} GB"
    )
