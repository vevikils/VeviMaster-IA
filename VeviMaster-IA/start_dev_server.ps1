# Script para iniciar el servidor de desarrollo de VeviMaster-IA
# con el entorno virtual Python 3.11

Write-Host "=== VeviMaster-IA - Servidor de Desarrollo ===" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
Write-Host "Activando entorno virtual Python 3.11..." -ForegroundColor Yellow
& ".\.venv_py311\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: No se pudo activar el entorno virtual" -ForegroundColor Red
    Write-Host "Asegúrate de que existe el directorio .venv_py311" -ForegroundColor Red
    exit 1
}

Write-Host "Entorno virtual activado correctamente" -ForegroundColor Green
Write-Host ""

# Cambiar al directorio del proyecto Django
Set-Location "vevi_mastering"

# Verificar que manage.py existe
if (-not (Test-Path "manage.py")) {
    Write-Host "Error: No se encontró manage.py en vevi_mastering/" -ForegroundColor Red
    exit 1
}

# Mostrar información
Write-Host "Iniciando servidor Django en http://localhost:8000" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
