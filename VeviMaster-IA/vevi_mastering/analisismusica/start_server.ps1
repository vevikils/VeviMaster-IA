# Script para iniciar el servidor Django
# Ejecuta este script para iniciar la interfaz web

Write-Host "Iniciando servidor Django..." -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "ERROR: No se encontró el entorno virtual. Ejecuta primero setup_python311.ps1" -ForegroundColor Red
    exit 1
}

# Verificar que Django esté instalado
$djangoInstalled = python -c "import django; print(django.get_version())" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Django no está instalado. Ejecuta: pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host "Django $djangoInstalled instalado" -ForegroundColor Green
Write-Host ""

# Crear directorios necesarios
if (-not (Test-Path "media")) {
    New-Item -ItemType Directory -Path "media" | Out-Null
    Write-Host "Directorio 'media' creado" -ForegroundColor Yellow
}

# Ejecutar migraciones si es necesario
Write-Host "Verificando migraciones..." -ForegroundColor Yellow
python manage.py migrate --noinput | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servidor iniciándose..." -ForegroundColor Cyan
Write-Host "  Abre tu navegador en:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver

