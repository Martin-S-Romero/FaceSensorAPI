from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.src.api.schemas import UrlProcessRequest, CensorshipMode, MediaType
from app.src.utils.dependencies import get_storage_service, get_face_censor_service
from app.src.services.storage_service import StorageService
from app.src.services.face_censor_service import FaceCensorService


router = APIRouter()


@router.post("/image", response_class=FileResponse)
async def process_image(
    file: UploadFile = File(...),
    mode: CensorshipMode = CensorshipMode.BLUR,
    cut: bool = False,
    expand: int = 10,
    blur_strength: int = 55,
    pixel_size: int = 10,
    storage: StorageService = Depends(get_storage_service),
    censor_service: FaceCensorService = Depends(get_face_censor_service),
):
    input_path = await storage.save_upload_image(file)
    output_path = storage.build_output_image_path(file.filename)
    result_path = censor_service.censor_image(
        input_path=input_path,
        output_path=output_path,
        mode=mode,
        cut=cut,
        expand=expand,
        blur_strength=blur_strength,
        pixel_size=pixel_size,
    )
    return FileResponse(path=str(result_path), filename=result_path.name)


@router.post("/video", response_class=FileResponse)
async def process_video(
    file: UploadFile = File(...),
    mode: CensorshipMode = CensorshipMode.BLUR,
    cut: bool = False,
    expand: int = 10,
    blur_strength: int = 55,
    pixel_size: int = 10,
    storage: StorageService = Depends(get_storage_service),
    censor_service: FaceCensorService = Depends(get_face_censor_service),
):
    input_path = await storage.save_upload_video(file)
    output_path = storage.build_output_video_path(file.filename)
    result_path = censor_service.censor_video(
        input_path=input_path,
        output_path=output_path,
        mode=mode,
        cut=cut,
        expand=expand,
        blur_strength=blur_strength,
        pixel_size=pixel_size,
    )
    return FileResponse(path=str(result_path), filename=result_path.name)


@router.post("/url", response_class=FileResponse)
async def process_url(
    payload: UrlProcessRequest,
    storage: StorageService = Depends(get_storage_service),
    censor_service: FaceCensorService = Depends(get_face_censor_service),
):
    input_path = await storage.download_remote(
        url=str(payload.url), media_type=payload.media_type
    )

    if payload.media_type == MediaType.IMAGE:
        output_path = storage.build_output_image_path(input_path.name)
        result_path = censor_service.censor_image(
            input_path=input_path,
            output_path=output_path,
            mode=payload.mode,
            cut=payload.cut,
            expand=payload.expand,
            blur_strength=payload.blur_strength,
            pixel_size=payload.pixel_size,
        )
    else:
        output_path = storage.build_output_video_path(input_path.name)
        result_path = censor_service.censor_video(
            input_path=input_path,
            output_path=output_path,
            mode=payload.mode,
            cut=payload.cut,
            expand=payload.expand,
            blur_strength=payload.blur_strength,
            pixel_size=payload.pixel_size,
        )

    return FileResponse(path=str(result_path), filename=result_path.name)
