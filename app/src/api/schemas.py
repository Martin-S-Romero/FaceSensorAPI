from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class CensorshipMode(str, Enum):
    BLUR = "blur"
    BLACK = "black"
    PIXELATE = "pixelate"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class UrlProcessRequest(BaseModel):
    url: HttpUrl
    media_type: MediaType
    mode: CensorshipMode = CensorshipMode.BLUR
    cut: bool = False
    expand: int = 10
    blur_strength: int = 55
    pixel_size: int = 10


class ProcessResponse(BaseModel):
    output_path: str
