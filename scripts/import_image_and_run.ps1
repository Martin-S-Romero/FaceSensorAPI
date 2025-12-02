param(
    [string]$TarPath = "tesis20-api.tar"
)

$ErrorActionPreference = "Stop"

Write-Host "[IMPORT] Cargando imagen Docker desde '$TarPath'" -ForegroundColor Cyan

if (-not (Test-Path $TarPath)) {
    Write-Error "[IMPORT] No se encontró el archivo '$TarPath'. Colócalo en este directorio o pasa la ruta correcta con -TarPath."
    exit 1
}

# Cargar imagen
docker load -i $TarPath

Write-Host "[IMPORT] Imagen cargada. Imágenes disponibles:" -ForegroundColor Yellow
docker images

# Levantar stack con docker compose (suponiendo que el repo está clonado)
Write-Host "[IMPORT] Levantando contenedor con 'docker compose up -d'..." -ForegroundColor Cyan

docker compose up -d

Write-Host "[IMPORT] Contenedores en ejecución:" -ForegroundColor Yellow
docker ps

Write-Host "[IMPORT] API disponible (si docker-compose.yml usa el mismo mapeo de puertos):" -ForegroundColor Green
Write-Host "  Healthcheck: http://127.0.0.1:8001/health" -ForegroundColor Green
Write-Host "  Swagger UI:  http://127.0.0.1:8001/docs" -ForegroundColor Green
