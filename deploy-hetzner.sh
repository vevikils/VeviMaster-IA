#!/bin/bash

# Script de despliegue para Hetzner
# Ejecuta este script en tu servidor Hetzner

echo "==================================="
echo "Desplegando VeviMaster-IA en Hetzner"
echo "==================================="

# Actualizar sistema
echo "Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
echo "Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Instalar Docker Compose
echo "Instalando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clonar repositorio
echo "Clonando repositorio..."
if [ ! -d "VeviMaster-IA" ]; then
    git clone https://github.com/vevikils/VeviMaster-IA.git
fi

cd VeviMaster-IA

# Configurar variables de entorno
echo "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.docker .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus valores:"
    echo "   nano .env"
    echo ""
    read -p "Presiona Enter cuando hayas configurado el archivo .env..."
fi

# Construir y ejecutar
echo "Construyendo imagen Docker..."
docker-compose build

echo "Iniciando contenedores..."
docker-compose up -d

# Ejecutar migraciones
echo "Ejecutando migraciones de Django..."
docker-compose exec web python manage.py migrate

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
docker-compose exec web python manage.py collectstatic --noinput

echo ""
echo "==================================="
echo "✅ Despliegue completado!"
echo "==================================="
echo ""
echo "Tu aplicación está corriendo en: http://$(curl -s ifconfig.me):8000"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Detener: docker-compose down"
echo "  - Reiniciar: docker-compose restart"
echo ""
