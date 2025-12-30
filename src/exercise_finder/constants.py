from exercise_finder.enums import ExamLevel, ImageType

pdf_acronym_to_level_mapping = {
    "vw": ExamLevel.VWO,
    "hv": ExamLevel.HAVO,
    "vm": ExamLevel.VMBO,
}

image_suffixes = {
    f".{ImageType.PNG.value}",
    f".{ImageType.JPG.value}",
    f".{ImageType.JPEG.value}",
    f".{ImageType.WEBP.value}",
}

# System/hidden files to ignore when processing directories
IGNORED_FILES = {
    ".DS_Store",     # macOS
    ".gitkeep",      # Git placeholder
    "Thumbs.db",     # Windows
    "desktop.ini",   # Windows
}

# Session expiration time in seconds (24 hours)
SESSION_EXPIRATION_SECONDS = 24 * 60 * 60
