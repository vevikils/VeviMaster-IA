# Script para preparar el despliegue en Hetzner
# VeviMaster-IA - Preparacion para Hetzner

param(
    [Parameter(Mandatory = $false)]
    [string]$ServerIP
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VeviMaster-IA - Preparar Hetzner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se proporciono la IP del servidor
if (-not $ServerIP) {
    Write-Host "Uso: .\prepare_hetzner.ps1 -ServerIP <IP_DEL_SERVIDOR>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ejemplo:" -ForegroundColor Yellow
    Write-Host "  .\prepare_hetzner.ps1 -ServerIP 95.217.161.141" -ForegroundColor White
    Write-Host ""
    $ServerIP = Read-Host "Ingresa la IP de tu servidor Hetzner"
    
    if (-not $ServerIP) {
        Write-Host "[ERROR] Debes proporcionar la IP del servidor" -ForegroundColor Red
        exit 1
    }
}

Write-Host "IP del servidor: $ServerIP" -ForegroundColor Green
Write-Host ""

# Generar SECRET_KEY
Write-Host "Generando SECRET_KEY segura..." -ForegroundColor Yellow
$secretKey = -join ((48..57) + (65..90) + (97..122) + @(33, 35, 36, 37, 38, 42, 43, 45, 61, 63, 64, 94) | Get-Random -Count 50 | ForEach-Object { [char]$_ })
Write-Host "[OK] SECRET_KEY generada" -ForegroundColor Green
Write-Host ""

# Crear archivo .env.hetzner
Write-Host "Creando archivo .env.hetzner..." -ForegroundColor Yellow
$envContent = @"
DEBUG=False
SECRET_KEY=$secretKey
ALLOWED_HOSTS=$ServerIP
DATABASE_URL=sqlite:///db.sqlite3
"@

$envContent | Out-File -FilePath ".env.hetzner" -Encoding UTF8 -NoNewline
Write-Host "[OK] Archivo .env.hetzner creado" -ForegroundColor Green
Write-Host ""

# Mostrar contenido
Write-Host "Contenido del archivo .env.hetzner:" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Get-Content ".env.hetzner"
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host ""

# Verificar si Git esta instalado
Write-Host "Verificando Git..." -ForegroundColor Yellow
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Git esta instalado" -ForegroundColor Green
    
    # Verificar estado del repositorio
    Write-Host ""
    Write-Host "Estado del repositorio:" -ForegroundColor Cyan
    git status --short
    
    Write-Host ""
    $commit = Read-Host "Deseas hacer commit y push de los cambios? (s/n)"
    
    if ($commit -eq "s" -or $commit -eq "S") {
        Write-Host ""
        Write-Host "Agregando archivos..." -ForegroundColor Yellow
        git add .
        
        $message = Read-Host "Mensaje del commit (Enter para usar mensaje por defecto)"
        if (-not $message) {
            $message = "Preparar para despliegue en Hetzner"
        }
        
        Write-Host "Haciendo commit..." -ForegroundColor Yellow
        git commit -m $message
        
        Write-Host "Haciendo push..." -ForegroundColor Yellow
        git push
        
        Write-Host "[OK] Cambios subidos a GitHub" -ForegroundColor Green
    }
}
else {
    Write-Host "[ADVERTENCIA] Git no esta instalado" -ForegroundColor Yellow
    Write-Host "Necesitaras subir los cambios manualmente a GitHub" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  [OK] PREPARACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Conectate a tu servidor Hetzner:" -ForegroundColor White
Write-Host "   ssh root@$ServerIP" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Ejecuta el script de despliegue:" -ForegroundColor White
Write-Host "   curl -O https://raw.githubusercontent.com/vevikils/VeviMaster-IA/main/deploy-hetzner.sh" -ForegroundColor Yellow
Write-Host "   chmod +x deploy-hetzner.sh" -ForegroundColor Yellow
Write-Host "   ./deploy-hetzner.sh" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Cuando te pida configurar .env, copia el contenido de .env.hetzner" -ForegroundColor White
Write-Host ""
Write-Host "4. Accede a tu aplicacion en:" -ForegroundColor White
Write-Host "   http://$ServerIP:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para mas detalles, consulta: DEPLOY_HETZNER.md" -ForegroundColor Cyan
Write-Host ""
