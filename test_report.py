from pathlib import Path

from app.report import generate_report


report = generate_report(Path.home())


print()
print("LinuxGuard Unified Storage Report")
print("=" * 70)

stats = report["statistics"]

print()
print("SYSTEM SUMMARY")
print("-" * 70)

print(f"Total Files:       {stats['total_files']}")
print(f"Total Directories: {stats['total_directories']}")
print(f"Total Size:        {stats['total_size'] / (1024 ** 3):.2f} GB")


print()
print("TOP DIRECTORIES")
print("-" * 70)

for item in report["directories"][:10]:

    print(
        f"{item['name']:<25}"
        f"{item['size'] / (1024 ** 3):>8.2f} GB   "
        f"{item['risk']:<10}"
    )


print()
print("FILE CATEGORIES")
print("-" * 70)

for category, data in report["categories"].items():

    print(
        f"{category:<15}"
        f"{data['count']:>8} files   "
        f"{data['size'] / (1024 ** 3):>8.2f} GB"
    )


print()
print("LARGEST FILES")
print("-" * 70)

for file_path, size in report["largest_files"]:

    print(
        f"{size / (1024 ** 3):>8.2f} GB   "
        f"{file_path}"
    )
