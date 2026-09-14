FILE_CATEGORIES = {

    "Video": {
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".flv",
        ".webm",
    },

    "Image": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".svg",
    },

    "Document": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".odt",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    },

    "Archive": {
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
    },

    "Code": {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".html",
        ".css",
        ".sql",
        ".sh",
    },
}


def get_file_category(extension):

    extension = extension.lower()

    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:
            return category

    return "Other"
