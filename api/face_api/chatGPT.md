Aquí tienes **la forma más limpia, moderna y mantenible** de convertir tu clase `FaceCensor` en una **API completa** usando **FastAPI**, permitiendo:

✔ subir imágenes
✔ subir videos
✔ enviar URLs
✔ configurar parámetros (`mode`, `expand`, `cut`, etc.)
✔ devolver archivo procesado
✔ endpoints separados para imagen y video

---

# ✅ **1. Estructura recomendada del proyecto**

```
/face_api
│
├── main.py
├── face_censor.py   ← tu clase aquí
├── requirements.txt
└── processed/        ← salidas generadas
```

---

# ✅ **2. Archivo `face_censor.py`**

Copia tu clase exactamente como está (no tienes que modificar nada).

---

# ✅ **3. Archivo `main.py` — API FastAPI lista para producción**

```python
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from face_censor import FaceCensor
import uuid
import os
import shutil

app = FastAPI(title="FaceCensor API")

OUTPUT_DIR = "processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_upload_file_tmp(upload_file: UploadFile) -> str:
    """Guarda archivo subido en un archivo temporal."""
    ext = os.path.splitext(upload_file.filename)[1]
    tmp_path = f"/tmp/{uuid.uuid4()}{ext}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return tmp_path


# =========================== IMAGEN ===============================

@app.post("/process/image")
async def process_image_api(
    file: UploadFile = File(None),
    url: str = Form(None),
    mode: str = Form("blur"),
    expand: int = Form(10),
    blur_strength: int = Form(55),
    pixel_size: int = Form(10),
    cut: bool = Form(False),
):
    """
    Procesa una imagen desde FILE o URL.
    """

    # 1) Resolver input
    if file:
        input_path = save_upload_file_tmp(file)
    elif url:
        input_path = url
    else:
        return {"error": "Debes enviar una imagen o una URL"}

    # 2) Construir clase
    censor = FaceCensor(
        mode=mode,
        expand=expand,
        blur_strength=blur_strength,
        pixel_size=pixel_size,
        cut=cut
    )

    # 3) Salida
    output_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.jpg")

    result = censor.process_image(input_path, output_path=output_path, show=False)

    if result is None:
        return {"error": "No se pudo procesar la imagen"}

    return FileResponse(output_path, media_type="image/jpeg")


# =========================== VIDEO ===============================

@app.post("/process/video")
async def process_video_api(
    file: UploadFile = File(None),
    url: str = Form(None),
    mode: str = Form("blur"),
    expand: int = Form(10),
    blur_strength: int = Form(55),
    pixel_size: int = Form(10),
    cut: bool = Form(False),
):
    """
    Procesa un video desde FILE o URL.
    """

    # 1) Resolver input
    if file:
        input_path = save_upload_file_tmp(file)
    elif url:
        input_path = url
    else:
        return {"error": "Debes enviar un video o una URL"}

    # 2) Instancia de FaceCensor
    censor = FaceCensor(
        mode=mode,
        expand=expand,
        blur_strength=blur_strength,
        pixel_size=pixel_size,
        cut=cut
    )

    # 3) Salida
    output_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.mp4")

    censor.process_video(input_path, output_path=output_path, show=False)

    return FileResponse(output_path, media_type="video/mp4")
```

---

# ✅ **4. Instalar dependencias**

En `requirements.txt`:

```
fastapi
uvicorn
opencv-python
mediapipe
numpy
requests
```

---

# 🚀 **5. Correr la API**

```
uvicorn main:app --reload
```

FastAPI estará en:

➡ **[http://localhost:8000](http://localhost:8000)**

Documentación interactiva automática:

➡ **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI)

---

# 🎯 **6. Ejemplos de uso**

### **Procesar imagen desde URL**

```
curl -X POST "http://localhost:8000/process/image" \
-F "url=https://ejemplo.com/foto.jpg"
```

### **Procesar imagen enviando archivo**

```
curl -X POST "http://localhost:8000/process/image" \
-F "file=@cara.png"
```

### **Procesar video**

```
curl -X POST "http://localhost:8000/process/video" \
-F "file=@video.mp4" \
-F "cut=true" \
-F "mode=pixelate"
```