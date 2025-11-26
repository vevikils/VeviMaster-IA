# Script para configurar Docker localmente en Windows
# VeviMaster-IA - Configuracion Docker Local

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VeviMaster-IA - Setup Docker Local" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker esta instalado
Write-Host "Verificando Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Docker esta instalado" -ForegroundColor Green
    docker --version
}
else {
    Write-Host "[ERROR] Docker no esta instalado" -ForegroundColor Red
    Write-Host "Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Verificar si Docker esta corriendo
Write-Host "Verificando si Docker esta corriendo..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker esta corriendo" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker no esta corriendo" -ForegroundColor Red
    Write-Host "Por favor inicia Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Crear archivo .env si no existe
if (-not (Test-Path ".env")) {
    Write-Host "Creando archivo .env..." -ForegroundColor Yellow
    $envContent = @"
DEBUG=False
SECRET_KEY=b%09d6c$71&cb8h3^tjwe5f0f1y6km5y^ttfp*9sz=6d4n6xb(
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline
    Write-Host "[OK] Archivo .env creado" -ForegroundColor Green
}
else {
    Write-Host "[OK] Archivo .env ya existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Construyendo imagen Docker..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Esto puede tardar varios minutos la primera vez..." -ForegroundColor Yellow
Write-Host ""

# Construir imagen
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Imagen construida exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Iniciando contenedor..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Iniciar contenedor
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Contenedor iniciado exitosamente" -ForegroundColor Green
        Write-Host ""
        
        # Esperar un momento para que el contenedor inicie
        Write-Host "Esperando a que el servidor inicie..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Ejecutar migraciones
        Write-Host ""
        Write-Host "Ejecutando migraciones de Django..." -ForegroundColor Yellow
        docker-compose exec web python manage.py migrate
        
        # Recolectar archivos estaticos
        Write-Host ""
        Write-Host "Recolectando archivos estaticos..." -ForegroundColor Yellow
        docker-compose exec web python manage.py collectstatic --noinput
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  [OK] CONFIGURACION COMPLETADA" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Tu aplicacion esta corriendo en:" -ForegroundColor Cyan
        Write-Host "  http://localhost:8000" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Comandos utiles:" -ForegroundColor Cyan
        Write-Host "  Ver logs:      docker-compose logs -f" -ForegroundColor White
        Write-Host "  Detener:       docker-compose down" -ForegroundColor White
        Write-Host "  Reiniciar:     docker-compose restart" -ForegroundColor White
        Write-Host "  Ver estado:    docker-compose ps" -ForegroundColor White
        Write-Host ""
        
        # Intentar abrir en el navegador
        Write-Host "Abriendo navegador..." -ForegroundColor Yellow
        Start-Process "http://localhost:8000"
        
    }
    else {
        Write-Host ""
        Write-Host "[ERROR] Error al iniciar el contenedor" -ForegroundColor Red
        Write-Host "Revisa los logs con: docker-compose logs" -ForegroundColor Yellow
    }
}
else {
    Write-Host ""
    Write-Host "[ERROR] Error al construir la imagen" -ForegroundColor Red
    Write-Host "Revisa los errores arriba" -ForegroundColor Yellow
}
