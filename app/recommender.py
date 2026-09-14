def get_recommendation(name, category, risk, size_gb):

    if risk == "PROTECTED":
        return "Do not delete automatically."

    if category == "Cache":
        if size_gb >= 1:
            return "Large cache detected. Review for cleanup."
        else:
            return "Cache is small. No action needed."

    if category == "Downloads":
        if size_gb >= 1:
            return "Review old downloads and remove unnecessary files."
        else:
            return "Downloads size is currently low."

    if size_gb >= 10:
        return "Large personal directory. Review files for archiving."

    if size_gb >= 5:
        return "Moderately large directory. Review if cleanup is needed."

    return "No immediate action required."
