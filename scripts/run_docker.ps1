$ErrorActionPreference = "Stop"

Write-Host "[DOCKER] Construyendo y levantando contenedor media-censorship-api" -ForegroundColor Cyan

# Ir al directorio del script
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Set-Location ..  # raíz del proyecto

# Levantar stack
docker compose up --build -d

Write-Host "[DOCKER] Contenedores en ejecución:" -ForegroundColor Yellow
docker ps

Write-Host "[DOCKER] API disponible en:" -ForegroundColor Green
Write-Host "  Healthcheck: http://127.0.0.1:8001/health" -ForegroundColor Green
Write-Host "  Swagger UI:  http://127.0.0.1:8001/docs" -ForegroundColor Green
