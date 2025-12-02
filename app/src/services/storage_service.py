import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.src.api.schemas import MediaType


class StorageService:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        if base_dir is None:
            # project_root/app/src/services -> go up 3 levels
            base_dir = Path(__file__).resolve().parents[3] / "storage"
        self.base_dir = base_dir
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        for sub in [
            self.input_dir / "images",
            self.input_dir / "videos",
            self.output_dir / "images",
            self.output_dir / "videos",
        ]:
            sub.mkdir(parents=True, exist_ok=True)

    async def save_upload_image(self, file: UploadFile) -> Path:
        ext = os.path.splitext(file.filename or "")[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        dest = self.input_dir / "images" / filename
        content = await file.read()
        dest.write_bytes(content)
        return dest

    async def save_upload_video(self, file: UploadFile) -> Path:
        ext = os.path.splitext(file.filename or "")[1] or ".mp4"
        filename = f"{uuid.uuid4().hex}{ext}"
        dest = self.input_dir / "videos" / filename
        content = await file.read()
        dest.write_bytes(content)
        return dest

    async def download_remote(self, url: str, media_type: MediaType) -> Path:
        import requests

        response = requests.get(url, timeout=15)
        response.raise_for_status()

        if media_type == MediaType.IMAGE:
            subdir = self.input_dir / "images"
            default_ext = ".jpg"
        else:
            subdir = self.input_dir / "videos"
            default_ext = ".mp4"

        subdir.mkdir(parents=True, exist_ok=True)
        ext = default_ext
        filename = f"{uuid.uuid4().hex}{ext}"
        dest = subdir / filename
        dest.write_bytes(response.content)
        return dest

    def build_output_image_path(self, original_name: str) -> Path:
        ext = os.path.splitext(original_name or "")[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        return self.output_dir / "images" / filename

    def build_output_video_path(self, original_name: str) -> Path:
        ext = os.path.splitext(original_name or "")[1] or ".mp4"
        filename = f"{uuid.uuid4().hex}{ext}"
        return self.output_dir / "videos" / filename
