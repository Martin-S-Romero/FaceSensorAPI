param(
    [string]$ImageName = "tesis20-api",
    [string]$Output   = "tesis20-api.tar"
)

$ErrorActionPreference = "Stop"

Write-Host "[EXPORT] Guardando imagen Docker '$ImageName' en '$Output'" -ForegroundColor Cyan

# Comprobar que la imagen existe
$img = docker images --format "{{.Repository}}:{{.Tag}}" | Where-Object { $_ -like "$ImageName*" }
if (-not $img) {
    Write-Error "[EXPORT] No se encontró la imagen '$ImageName'. Ejecuta primero 'docker images' y verifica el nombre."
    exit 1
}

# Guardar imagen a tar
docker save -o $Output $ImageName

Write-Host "[EXPORT] Imagen guardada en '$Output'." -ForegroundColor Green
Write-Host "[EXPORT] Ahora puedes comprimirla (zip/7z) y compartirla." -ForegroundColor Yellow
