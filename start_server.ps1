# Script para iniciar el servidor con Python 3.11
# Este script activa el entorno virtual correcto y ejecuta el servidor

$venvPath = ".venv311\Scripts\Activate.ps1"
$projectPath = "vevi_mastering"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "VeviMaster-IA con Análisis Musical" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si el entorno virtual existe
if (-not (Test-Path $venvPath)) {
    Write-Host "ERROR: No se encontró el entorno virtual de Python 3.11" -ForegroundColor Red
    Write-Host "Por favor, ejecuta primero: setup_python311.ps1" -ForegroundColor Yellow
    exit 1
}

# Activar el entorno virtual
Write-Host "Activando entorno virtual de Python 3.11..." -ForegroundColor Green
& $venvPath

# Cambiar al directorio del proyecto
Set-Location $projectPath

# Verificar migraciones
Write-Host ""
Write-Host "Verificando migraciones de base de datos..." -ForegroundColor Green
python manage.py migrate --check 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Aplicando migraciones..." -ForegroundColor Yellow
    python manage.py migrate
}

# Iniciar el servidor
Write-Host ""
Write-Host "Iniciando servidor Django..." -ForegroundColor Green
Write-Host ""
Write-Host "Accede a las siguientes URLs:" -ForegroundColor Cyan
Write-Host "  - Mastering:        http://127.0.0.1:8080/" -ForegroundColor White
Write-Host "  - Análisis Musical: http://127.0.0.1:8080/analyzer/" -ForegroundColor White
Write-Host "  - Admin:            http://127.0.0.1:8080/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver 8080

