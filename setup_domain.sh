#!/bin/bash

# Script de configuración de dominio para VeviMaster IA
# Uso: ./setup_domain.sh

set -e  # Salir si hay algún error

DOMAIN="vevimaster.com"
APP_PORT="8001"
EMAIL="admin@vevimaster.com"  # Cambia esto a tu email real

echo "=========================================="
echo "  Configurando $DOMAIN"
echo "=========================================="

# 1. Actualizar sistema e instalar dependencias
echo ""
echo "[1/6] Instalando Nginx y Certbot..."
apt update
apt install -y nginx certbot python3-certbot-nginx

# 2. Crear configuración de Nginx
echo ""
echo "[2/6] Creando configuración de Nginx..."
cat > /etc/nginx/sites-available/vevimaster <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;
    client_body_timeout 300s;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    location /static/ {
        alias /root/VeviMaster-IA/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /root/VeviMaster-IA/media/;
        expires 7d;
    }
}
EOF

# 3. Activar el sitio
echo ""
echo "[3/6] Activando el sitio..."
ln -sf /etc/nginx/sites-available/vevimaster /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 4. Verificar configuración de Nginx
echo ""
echo "[4/6] Verificando configuración de Nginx..."
nginx -t

# 5. Reiniciar Nginx
echo ""
echo "[5/6] Reiniciando Nginx..."
systemctl restart nginx
systemctl enable nginx

# 6. Configurar HTTPS con Let's Encrypt
echo ""
echo "[6/6] Configurando HTTPS (esto puede tardar un minuto)..."
echo ""
echo "IMPORTANTE: Asegúrate de que el DNS ya esté propagado."
echo "Puedes verificarlo con: dig $DOMAIN"
echo ""
read -p "¿Continuar con la configuración de HTTPS? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]
then
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect
    echo ""
    echo "✅ Certificado SSL instalado correctamente"
else
    echo "⏭️  Saltando configuración de HTTPS"
    echo "   Puedes ejecutarlo más tarde con:"
    echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

echo ""
echo "=========================================="
echo "  ✅ Configuración completada"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. Actualiza el archivo .env con:"
echo "   ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,46.62.227.207"
echo ""
echo "2. Reinicia Docker:"
echo "   cd ~/VeviMaster-IA && docker-compose restart"
echo ""
echo "3. Visita: https://$DOMAIN"
echo ""
