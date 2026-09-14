from pathlib import Path

from app.cleanup import (
    is_protected,
    get_cleanup_candidates,
)


home = Path.home()


print("LinuxGuard Cleanup Scanner")
print("=" * 50)


test_path = home / ".ssh"

print()
print("Testing protected directory:")
print(test_path)

print(
    "Protected:",
    is_protected(test_path)
)


print()
print("Scanning cleanup candidates...")


candidates = get_cleanup_candidates(home)


print(
    f"Found {len(candidates)} cleanup candidates."
)


print()
print("First 10 candidates:")
print("-" * 50)


for item in candidates[:10]:
    print(item)
