#!/bin/sh

# Detener el script si hay errores
set -e

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Aplicando migraciones de base de datos..."
python manage.py migrate

echo "Creando superusuario..."
# Asumimos que create_superuser.py maneja la verificación si ya existe
python create_superuser.py

echo "Configurando dominio del sitio..."
python manage.py shell -c "from django.contrib.sites.models import Site; Site.objects.update_or_create(id=1, defaults={'domain': 'vevimaster.com', 'name': 'VeviMaster IA'})"

echo "Configurando Google OAuth..."
python manage.py setup_google_oauth

echo "Iniciando servidor..."
exec "$@"
