# Script para configurar el entorno con Python 3.11
# Ejecuta este script después de instalar Python 3.11

Write-Host "Verificando Python 3.11..." -ForegroundColor Cyan

# Verificar si Python 3.11 está instalado
try {
    $pythonVersion = python3.11 --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python 3.11 no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor, instala Python 3.11 desde: https://www.python.org/downloads/release/python-31111/" -ForegroundColor Yellow
    Write-Host "Asegúrate de marcar 'Add Python 3.11 to PATH' durante la instalación" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nCreando entorno virtual..." -ForegroundColor Cyan
python3.11 -m venv .venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
    exit 1
}

Write-Host "Activando entorno virtual..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host "Actualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host "`nInstalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n¡Instalación completada exitosamente!" -ForegroundColor Green
    Write-Host "`nPara usar el programa:" -ForegroundColor Cyan
    Write-Host "1. Activa el entorno virtual: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "2. Ejecuta: python analyze.py --audio `"ruta/al/archivo.mp3`"" -ForegroundColor Yellow
} else {
    Write-Host "`nERROR: Hubo problemas al instalar las dependencias" -ForegroundColor Red
    exit 1
}


