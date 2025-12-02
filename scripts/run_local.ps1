param(
    [switch]$Reinstall
)

$ErrorActionPreference = "Stop"

Write-Host "[LOCAL] Iniciando servicio Media Censorship (modo desarrollo)" -ForegroundColor Cyan

# Ir al directorio del script
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Set-Location ..  # subir a la raíz del proyecto

# Crear venv si no existe
if (-not (Test-Path ".venv")) {
    Write-Host "[LOCAL] Creando entorno virtual .venv..." -ForegroundColor Yellow
    python -m venv .venv
    $Reinstall = $true
}

$venvPython = Join-Path ".venv" "Scripts/python.exe"
$venvPip    = Join-Path ".venv" "Scripts/pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "[LOCAL] No se encontró .venv/Scripts/python.exe. Verifica tu instalación de Python."
    exit 1
}

# Instalar dependencias si se pide explícitamente o si es la primera vez
if ($Reinstall -or -not (Test-Path "requirements.installed")) {
    Write-Host "[LOCAL] Instalando dependencias desde requirements.txt..." -ForegroundColor Yellow
    & $venvPip install --upgrade pip
    & $venvPip install -r requirements.txt
    "ok" | Out-File -Encoding ascii requirements.installed
}

Write-Host "[LOCAL] Levantando Uvicorn en http://127.0.0.1:8000 ..." -ForegroundColor Green
& $venvPython -m uvicorn app.main:app --reload
