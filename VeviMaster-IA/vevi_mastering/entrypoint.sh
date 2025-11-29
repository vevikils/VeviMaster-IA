#!/bin/sh

# Detener el script si hay errores
set -e

echo "Aplicando migraciones de base de datos..."
python manage.py migrate

echo "Creando superusuario..."
# Asumimos que create_superuser.py maneja la verificación si ya existe
python create_superuser.py

echo "Configurando dominio del sitio..."
python manage.py shell -c "from django.contrib.sites.models import Site; Site.objects.update_or_create(id=1, defaults={'domain': 'vevimaster-ia.onrender.com', 'name': 'VeviMaster IA'})"

echo "Iniciando servidor..."
exec "$@"
