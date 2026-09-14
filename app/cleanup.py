import os
from pathlib import Path

from app.logger import get_logger
from app.database import engine
from app.repository import save_cleanup_action


SCAN_ROOT = Path(os.getenv("SCAN_ROOT", "/home")).resolve()
CLEANUP_ROOT = Path(
    os.getenv("CLEANUP_ROOT", "/cleanup-home")
).resolve()

PROTECTED_DIRECTORIES = {
    ".ssh",
    ".gnupg",
    ".config",
}

CLEANABLE_DIRECTORIES = {
    ".cache",
    "Downloads",
}


def is_protected(path):
    path = Path(path)

    for part in path.parts:
        if part in PROTECTED_DIRECTORIES:
            return True

    return False


def get_allowed_cleanup_roots(scan_root=None):
    """
    Return the exact cleanup directories that LinuxGuard is allowed
    to manage.

    Expected structure:

        SCAN_ROOT/
            <user>/
                Downloads/
                .cache/
    """

    root = Path(scan_root or SCAN_ROOT)

    if not root.exists() or not root.is_dir():
        return []

    allowed_roots = []

    try:
        for user_home in root.iterdir():
            if not user_home.is_dir():
                continue

            for directory in CLEANABLE_DIRECTORIES:
                target = user_home / directory

                if target.exists() and target.is_dir():
                    allowed_roots.append(target.resolve())

    except (PermissionError, OSError):
        pass

    return allowed_roots


def is_cleanup_allowed(path, scan_root=None):
    """
    Check whether a path belongs to one of the explicitly allowed
    cleanup directories.
    """

    path = Path(path)

    if not path.exists():
        return False

    if path.is_symlink():
        return False

    try:
        resolved_path = path.resolve()
    except (PermissionError, OSError):
        return False

    if is_protected(resolved_path):
        return False

    allowed_roots = get_allowed_cleanup_roots(scan_root)

    for allowed_root in allowed_roots:
        try:
            resolved_path.relative_to(allowed_root)
            return True
        except ValueError:
            continue

    return False


def get_cleanup_candidates(path):
    """
    Find files only inside:

        <user>/.cache
        <user>/Downloads

    Symlinks and protected locations are ignored.
    """

    path = Path(path)
    candidates = []

    if not path.exists() or not path.is_dir():
        return candidates

    try:
        user_homes = [
            item for item in path.iterdir()
            if item.is_dir() and not item.is_symlink()
        ]
    except (PermissionError, OSError):
        return candidates

    for user_home in user_homes:

        for directory in CLEANABLE_DIRECTORIES:

            target = user_home / directory

            if not target.exists():
                continue

            if not target.is_dir() or target.is_symlink():
                continue

            try:
                for item in target.rglob("*"):

                    if not item.is_file():
                        continue

                    if item.is_symlink():
                        continue

                    try:
                        if not is_cleanup_allowed(item, path):
                            continue

                        candidates.append(item.resolve())

                    except (PermissionError, OSError):
                        continue

            except (PermissionError, OSError):
                continue

    return candidates


def map_to_cleanup_path(file_path):
    """
    Convert a read-only scan path into its corresponding writable
    cleanup mount.

    Example:

        /host-home/alok/Downloads/test.txt

    becomes:

        /cleanup-home/alok/Downloads/test.txt
    """

    file_path = Path(file_path)

    if file_path.is_symlink():
        raise ValueError("Symlink cleanup is not allowed.")

    try:
        resolved_source = file_path.resolve(strict=True)
        relative_path = resolved_source.relative_to(SCAN_ROOT)
    except (FileNotFoundError, PermissionError, OSError, ValueError):
        raise ValueError("File is outside the configured scan root.")

    parts = relative_path.parts

    if len(parts) < 3:
        raise ValueError("Invalid cleanup path.")

    username = parts[0]
    cleanup_directory = parts[1]

    if cleanup_directory not in CLEANABLE_DIRECTORIES:
        raise ValueError("Directory is not approved for cleanup.")

    if username in {"", ".", ".."}:
        raise ValueError("Invalid user path.")

    cleanup_path = CLEANUP_ROOT.joinpath(*parts)

    try:
        resolved_cleanup = cleanup_path.resolve(strict=True)
    except (FileNotFoundError, PermissionError, OSError):
        raise ValueError("Writable cleanup path does not exist.")

    expected_root = (
        CLEANUP_ROOT
        / username
        / cleanup_directory
    ).resolve()

    try:
        resolved_cleanup.relative_to(expected_root)
    except ValueError:
        raise ValueError("Cleanup path escaped the allowed directory.")

    if resolved_cleanup.is_symlink():
        raise ValueError("Symlink cleanup is not allowed.")

    if not resolved_cleanup.is_file():
        raise ValueError("Cleanup target is not a file.")

    return resolved_cleanup


def cleanup_files(files, dry_run=True, confirmed=False):
    """
    Delete approved files.

    In Docker:

        scan path → writable cleanup path → delete

    In normal local execution, CLEANUP_ROOT can be configured to
    point to the same filesystem tree if desired.
    """

    logger = get_logger()
    deleted_files = []

    if not confirmed and not dry_run:
        print("Cleanup cancelled: confirmation required.")
        return deleted_files

    for file_path in files:

        file_path = Path(file_path)

        try:
            if not is_cleanup_allowed(file_path):
                print(f"[BLOCKED] {file_path}")
                continue

            cleanup_path = map_to_cleanup_path(file_path)

        except (ValueError, PermissionError, OSError) as error:
            print(f"[BLOCKED] {file_path} | {error}")
            continue

        if dry_run:
            print(f"[DRY RUN] Would delete: {file_path}")
            continue

        try:
            cleanup_path.unlink()

            deleted_files.append(file_path)

            print(f"[DELETED] {file_path}")

            logger.info(
                f"CLEANUP | {file_path} | DELETED"
            )

            save_cleanup_action(
                engine,
                file_path,
                "DELETE",
                "SUCCESS"
            )

        except (PermissionError, OSError) as error:

            print(
                f"[ERROR] Could not delete "
                f"{file_path}: {error}"
            )

            save_cleanup_action(
                engine,
                file_path,
                "DELETE",
                "FAILED"
            )

    return deleted_files


def confirm_cleanup():
    answer = input(
        "Do you want to delete these files? [y/N]: "
    )

    return answer.strip().lower() in {"y", "yes"}

