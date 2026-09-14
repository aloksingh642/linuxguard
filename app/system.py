import os

import psutil


SYSTEM_DISK_PATH = os.getenv("SYSTEM_DISK_PATH", "/")


def get_disk_usage(path=None):
    """
    Return disk usage statistics for the configured Linux filesystem.

    In Docker deployments, SYSTEM_DISK_PATH can point to a read-only
    mount of the host filesystem.
    """

    target_path = path or SYSTEM_DISK_PATH

    usage = psutil.disk_usage(target_path)

    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent,
    }


def get_status(percent):
    if percent < 70:
        return "HEALTHY"
    elif percent <= 85:
        return "WARNING"
    else:
        return "CRITICAL"
