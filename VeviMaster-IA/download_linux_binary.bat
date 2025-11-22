@echo off
echo Descargando binario de Linux de phaselimiter...

REM Crear directorio si no existe
if not exist "vevi_mastering\app_files\phaselimiter\phaselimiter\bin" mkdir "vevi_mastering\app_files\phaselimiter\phaselimiter\bin"

REM Descargar usando curl
curl -L -o phaselimiter_linux.tar.xz https://github.com/ai-mastering/phaselimiter/releases/download/v0.2.0/release.tar.xz

REM Extraer
tar -xf phaselimiter_linux.tar.xz

REM Copiar solo el binario de Linux
copy "phaselimiter\bin\phase_limiter" "vevi_mastering\app_files\phaselimiter\phaselimiter\bin\"

REM Limpiar archivos temporales
rmdir /s /q phaselimiter
del phaselimiter_linux.tar.xz

echo Binario de Linux descargado correctamente!
pause
