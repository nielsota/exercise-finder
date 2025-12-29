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
