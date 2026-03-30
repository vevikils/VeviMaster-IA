# Script de configuración inicial para VeviMaster-IA con Análisis Musical
# Este script configura el entorno virtual de Python 3.11 e instala todas las dependencias

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuración de VeviMaster-IA" -ForegroundColor Cyan
Write-Host "con Análisis Musical (Python 3.11)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python 3.11 está instalado
$python311Path = "C:\Users\alfaswz\AppData\Local\Programs\Python\Python311\python.exe"

if (-not (Test-Path $python311Path)) {
    Write-Host "ERROR: Python 3.11 no está instalado en la ubicación esperada" -ForegroundColor Red
    Write-Host "Ubicación esperada: $python311Path" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Por favor, instala Python 3.11 desde:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/release/python-31111/" -ForegroundColor White
    Write-Host ""
    Write-Host "Asegúrate de marcar 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Python 3.11 encontrado" -ForegroundColor Green
& $python311Path --version
Write-Host ""

# Crear entorno virtual si no existe
$venvPath = ".venv311"
if (Test-Path $venvPath) {
    Write-Host "El entorno virtual ya existe en: $venvPath" -ForegroundColor Yellow
    $response = Read-Host "¿Deseas recrearlo? (s/N)"
    if ($response -eq "s" -or $response -eq "S") {
        Write-Host "Eliminando entorno virtual existente..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
    } else {
        Write-Host "Usando entorno virtual existente" -ForegroundColor Green
        Write-Host ""
        Write-Host "Si quieres instalar/actualizar dependencias, ejecuta:" -ForegroundColor Cyan
        Write-Host "  .\.venv311\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host "  pip install -r requirements.txt" -ForegroundColor White
        exit 0
    }
}

Write-Host "Creando entorno virtual con Python 3.11..." -ForegroundColor Green
& $python311Path -m venv $venvPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
Write-Host ""

# Activar el entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Green
& "$venvPath\Scripts\Activate.ps1"

# Actualizar pip
Write-Host ""
Write-Host "Actualizando pip..." -ForegroundColor Green
& "$venvPath\Scripts\python.exe" -m pip install --upgrade pip

# Instalar dependencias básicas de Django
Write-Host ""
Write-Host "Instalando dependencias básicas de Django..." -ForegroundColor Green
& "$venvPath\Scripts\pip.exe" install Django gunicorn whitenoise dj-database-url python-dotenv gdown

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar las dependencias básicas" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencias básicas instaladas" -ForegroundColor Green

# Instalar dependencias de análisis de música
Write-Host ""
Write-Host "Instalando dependencias de análisis de música (esto puede tardar varios minutos)..." -ForegroundColor Green
Write-Host "Instalando numpy, scipy, soundfile..." -ForegroundColor Yellow
& "$venvPath\Scripts\pip.exe" install "numpy>=1.19.0,<1.25" "scipy>=1.2.0" "soundfile>=0.10.0"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar numpy/scipy/soundfile" -ForegroundColor Red
    exit 1
}

Write-Host "✓ numpy, scipy, soundfile instalados" -ForegroundColor Green

Write-Host ""
Write-Host "Instalando librosa, tensorflow, colorama..." -ForegroundColor Yellow
Write-Host "(TensorFlow puede tardar varios minutos en descargarse e instalarse)" -ForegroundColor Yellow
& "$venvPath\Scripts\pip.exe" install "librosa>=0.7.0" "tensorflow>=2.5,<2.16" "colorama>=0.4"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar librosa/tensorflow/colorama" -ForegroundColor Red
    exit 1
}

Write-Host "✓ librosa, tensorflow, colorama instalados" -ForegroundColor Green

Write-Host ""
Write-Host "Instalando musicnn..." -ForegroundColor Yellow
& "$venvPath\Scripts\pip.exe" install musicnn==0.1.0

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo instalar musicnn" -ForegroundColor Red
    exit 1
}

Write-Host "✓ musicnn instalado" -ForegroundColor Green

# Ejecutar migraciones
Write-Host ""
Write-Host "Ejecutando migraciones de base de datos..." -ForegroundColor Green
cd vevi_mastering
& "..\$venvPath\Scripts\python.exe" manage.py makemigrations
& "..\$venvPath\Scripts\python.exe" manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron ejecutar las migraciones" -ForegroundColor Red
    cd ..
    exit 1
}

Write-Host "✓ Migraciones completadas" -ForegroundColor Green
cd ..

# Resumen final
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Configuración completada exitosamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar el servidor, ejecuta:" -ForegroundColor Cyan
Write-Host "  .\start_server.ps1" -ForegroundColor White
Write-Host ""
Write-Host "O manualmente:" -ForegroundColor Cyan
Write-Host "  .\.venv311\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  cd vevi_mastering" -ForegroundColor White
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Cyan
Write-Host "  - Mastering:        http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  - Análisis Musical: http://127.0.0.1:8000/analyzer/" -ForegroundColor White
Write-Host "  - Admin:            http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
