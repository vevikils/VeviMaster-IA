#!/bin/bash

# Configuración
DOMAIN="vevimaster.com"
APP_PORT="8001"

echo "--- Instalando Nginx y Certbot ---"
apt update
apt install -y nginx certbot python3-certbot-nginx

echo "--- Creando configuración de Nginx ---"
cat > /etc/nginx/sites-available/vevimaster <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;  # Permitir subidas grandes de audio

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Configuración para archivos estáticos (opcional si WhiteNoise falla)
    location /static/ {
        alias /root/VeviMaster-IA/staticfiles/;
    }
}
EOF

echo "--- Activando el sitio ---"
ln -sf /etc/nginx/sites-available/vevimaster /etc/nginx/sites-enabled/
# Desactivar el default si existe
rm -f /etc/nginx/sites-enabled/default

echo "--- Verificando y reiniciando Nginx ---"
nginx -t && systemctl restart nginx

echo "======================================================="
echo "¡Configuración de Nginx completada!"
echo "1. Asegúrate de que los DNS (Registro A) apunten a esta IP."
echo "2. Actualiza el ALLOWED_HOSTS en tu .env con: $DOMAIN"
echo "3. Para activar HTTPS (candadito), ejecuta:"
echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "======================================================="
