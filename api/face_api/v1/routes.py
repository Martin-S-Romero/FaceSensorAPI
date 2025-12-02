# v1/routes.py
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from api.face_api.auth import get_current_user
from api.face_api.face_censor import FaceCensor
import uuid
import os
import shutil
import time

router = APIRouter()  # ✔️ CORRECTO (NO crees FastAPI aquí)

BASE_DIR = "src"
os.makedirs(BASE_DIR, exist_ok=True)


def create_user_path(user_id: str, media_type: str) -> str:
    timestamp = str(int(time.time()))
    dir_path = os.path.join(BASE_DIR, user_id, media_type, timestamp)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def save_upload_file_tmp(upload_file: UploadFile) -> str:
    ext = os.path.splitext(upload_file.filename)[1]
    tmp_path = f"/tmp/{uuid.uuid4()}{ext}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return tmp_path


# =========================== IMAGEN (V1) ===============================

@router.post("/process/image")
async def process_image_api(
    user: str = Form(...),
    id: str = Form(...),
    file: UploadFile = File(None),
    url: str = Form(None),
    mode: str = Form("blur"),
    expand: int = Form(10),
    blur_strength: int = Form(55),
    pixel_size: int = Form(10),
    cut: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):

    if file:
        input_path = save_upload_file_tmp(file)
    elif url:
        input_path = url
    else:
        return {"error": "Debes enviar un archivo o una URL"}

    out_dir = create_user_path(user_id=user + id, media_type="img")
    output_path = os.path.join(out_dir, f"{uuid.uuid4()}.jpg")

    censor = FaceCensor(
        mode=mode,
        expand=expand,
        blur_strength=blur_strength,
        pixel_size=pixel_size,
        cut=cut
    )

    result = censor.process_image(input_path, output_path, show=False)

    if result is None:
        return {"error": "No se pudo procesar la imagen"}

    return FileResponse(output_path, media_type="image/jpeg")


# =========================== VIDEO (V1) ===============================

@router.post("/process/video")
async def process_video_api(
    user: str = Form(...),
    id: str = Form(...),
    file: UploadFile = File(None),
    url: str = Form(None),
    mode: str = Form("blur"),
    expand: int = Form(10),
    blur_strength: int = Form(55),
    pixel_size: int = Form(10),
    cut: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):

    if file:
        input_path = save_upload_file_tmp(file)
    elif url:
        input_path = url
    else:
        return {"error": "Debes enviar un archivo o una URL"}

    out_dir = create_user_path(user_id=user + id, media_type="video")
    output_path = os.path.join(out_dir, f"{uuid.uuid4()}.mp4")

    censor = FaceCensor(
        mode=mode,
        expand=expand,
        blur_strength=blur_strength,
        pixel_size=pixel_size,
        cut=cut
    )

    censor.process_video(input_path, output_path, show=False)

    return FileResponse(output_path, media_type="video/mp4")