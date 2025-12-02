from pathlib import Path

from app.src.api.schemas import CensorshipMode
from app.face_censor import FaceCensor


class FaceCensorService:
    def __init__(self) -> None:
        pass

    def censor_image(
        self,
        input_path: Path,
        output_path: Path,
        mode: CensorshipMode,
        cut: bool,
        expand: int,
        blur_strength: int,
        pixel_size: int,
    ) -> Path:
        censor = FaceCensor(
            mode=mode.value,
            blur_strength=blur_strength,
            expand=expand,
            pixel_size=pixel_size,
            cut=cut,
        )
        censor.process_image(str(input_path), output_path=str(output_path), show=False)
        return output_path

    def censor_video(
        self,
        input_path: Path,
        output_path: Path,
        mode: CensorshipMode,
        cut: bool,
        expand: int,
        blur_strength: int,
        pixel_size: int,
    ) -> Path:
        censor = FaceCensor(
            mode=mode.value,
            blur_strength=blur_strength,
            expand=expand,
            pixel_size=pixel_size,
            cut=cut,
        )
        censor.process_video(str(input_path), output_path=str(output_path), show=False)
        return output_path
