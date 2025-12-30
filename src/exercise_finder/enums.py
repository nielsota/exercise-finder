import enum

class ExamLevel(str, enum.Enum):
    VWO = "VWO"
    HAVO = "HAVO"
    VMBO = "VMBO"


class AgentName(str, enum.Enum):
    IMAGES_TO_QUESTION_AGENT = "images_to_question_agent"
    FORMAT_MULTIPART_QUESTION_AGENT = "format_multipart_question_agent"


class OpenAIModel(str, enum.Enum):
    GPT_5_MINI = "gpt-5-mini"
    GPT_4O = "gpt-4o"


class ImageType(str, enum.Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    WEBP = "webp"
