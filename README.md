# Media Censorship Service 

Sistema de censura de ojos y boca (imagen y video) basado en OpenCV + MediaPipe, expuesto como servicio FastAPI.

---

## 1. Inicio rápido (modo local)

### 1.1. Requisitos

- Python 3.10+ instalado
- `pip` disponible

### 1.2. Crear y activar entorno virtual

```bash
cd "tesis 2.0"
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
```

### 1.3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4. Ejecutar la API con Uvicorn

Desde la raíz del proyecto (`tesis 2.0`):

```bash
uvicorn app.main:app --reload
```

La API quedará escuchando en:

- `http://127.0.0.1:8000/health` → healthcheck
- `http://127.0.0.1:8000/docs` → Swagger UI (abre esta URL en una pestaña del navegador)

### 1.5. Probar endpoints principales

Ejemplos usando `curl.exe` (PowerShell):

#### Imagen local

```bash
curl.exe -i -X POST "http://127.0.0.1:8000/process/image" \
  -F "file=@ruta/a/tu_imagen.jpg" \
  -F "mode=blur"
```

#### Video local

```bash
curl.exe -i -X POST "http://127.0.0.1:8000/process/video" \
  -F "file=@ruta/a/tu_video.mp4" \
  -F "mode=blur"
```

#### URL remota (PowerShell)

```powershell
$body = @{
  url        = "https://ejemplo.com/imagen.jpg"
  media_type = "image"   # o "video"
  mode       = "blur"     # blur | black | pixelate
}

$json = $body | ConvertTo-Json -Compress

curl.exe -i -X POST "http://127.0.0.1:8000/process/url" `
  -H "Content-Type: application/json" `
  -d "$json"
```

---

## 2. Inicio rápido (modo contenedor Docker)

### 2.1. Requisitos

- Docker instalado
- Docker Compose disponible
- (Opcional) GPU NVIDIA configurada si quieres aprovechar la configuración de GPU

### 2.2. Construir imagen y levantar contenedor

Desde la raíz del proyecto (`tesis 2.0`):

```bash
docker compose up --build -d
```

- El servicio `api` se ejecuta dentro del contenedor `media-censorship-api`.
- El puerto interno `8000` se expone en el host como `8001`.
- La carpeta local `./storage` se monta en `/app/storage` dentro del contenedor.

### 2.3. Verificar que el contenedor está sano

```bash
docker ps
# y
curl.exe -i http://127.0.0.1:8001/health
```

Respuesta esperada:

```http
HTTP/1.1 200 OK
{"status":"ok"}
```

Swagger UI en contenedor:

- `http://127.0.0.1:8001/docs` → abre esta URL en una pestaña del navegador para ver y probar los endpoints

### 2.4. Probar endpoints desde el host (contra Docker)

#### Imagen local (usando volumen `./storage`)

```bash
curl.exe -i -X POST "http://127.0.0.1:8001/process/image" \
  -F "file=@storage/input/images/mi_imagen.jpg" \
  -F "mode=blur"
```

#### Video local

```bash
curl.exe -i -X POST "http://127.0.0.1:8001/process/video" \
  -F "file=@storage/input/videos/mi_video.mp4" \
  -F "mode=blur"
```

#### URL remota

```powershell
$body = @{
  url        = "https://ejemplo.com/imagen.jpg"
  media_type = "image"   # o "video"
  mode       = "blur"
}

$json = $body | ConvertTo-Json -Compress

curl.exe -i -X POST "http://127.0.0.1:8001/process/url" `
  -H "Content-Type: application/json" `
  -d "$json"
```

### 2.5. Apagar el contenedor

```bash
docker compose down
```

---

## 3. Scripts de inicio rápido (Windows / PowerShell)

Para simplificar el uso en entorno Windows se incluyen scripts en la carpeta `scripts/`.

### 3.1. Desarrollo local

```powershell
cd "c:\\Users\\Sheen\\Downloads\\tesis 2.0"
./scripts/run_local.ps1           # crea .venv, instala deps (si hace falta) y levanta Uvicorn
# o forzar reinstalación de dependencias
./scripts/run_local.ps1 -Reinstall
```

### 3.2. Docker

```powershell
cd "c:\\Users\\Sheen\\Downloads\\tesis 2.0"
./scripts/run_docker.ps1          # docker compose up --build -d y muestra URLs
```

### 3.3. Exportar imagen Docker para compartir

```powershell
cd "c:\\Users\\Sheen\\Downloads\\tesis 2.0"
./scripts/export_image.ps1                 # genera tesis20-api.tar por defecto
./scripts/export_image.ps1 -ImageName "tesis20-api" -Output "mi-imagen.tar"   # personalizado
```

### 3.4. Importar imagen y levantar contenedor (otra máquina)

```powershell
cd RUTA/AL/PROYECTO
./scripts/import_image_and_run.ps1          # asume tesis20-api.tar en el directorio
./scripts/import_image_and_run.ps1 -TarPath "mi-imagen.tar"   # ruta personalizada
```

Después de ejecutar el script de importación, la API quedará accesible en:

- `http://127.0.0.1:8001/health`
- `http://127.0.0.1:8001/docs`

Con esto tienes un flujo completo: correr localmente para desarrollo rápido y correr en contenedor para entornos más controlados o despliegue.
