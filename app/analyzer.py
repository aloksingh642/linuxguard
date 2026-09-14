PROTECTED_DIRECTORIES = {
    ".config",
    ".ssh",
    ".gnupg",
}

CACHE_DIRECTORIES = {
    ".cache",
}

DOWNLOAD_DIRECTORIES = {
    "Downloads",
}


def analyze_directory(name):

    if name in PROTECTED_DIRECTORIES:
        return {
            "category": "System/Security",
            "risk": "PROTECTED",
        }

    if name in CACHE_DIRECTORIES:
        return {
            "category": "Cache",
            "risk": "SAFE_TO_REVIEW",
        }

    if name in DOWNLOAD_DIRECTORIES:
        return {
            "category": "Downloads",
            "risk": "REVIEW",
        }

    return {
        "category": "Personal/Other",
        "risk": "REVIEW",
    }