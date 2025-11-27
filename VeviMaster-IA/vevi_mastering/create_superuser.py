import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vevi_mastering.settings')
django.setup()

User = get_user_model()
username = 'admin'
password = 'admin'
email = 'admin@example.com'

if not User.objects.filter(username=username).exists():
    print(f"Creando superusuario {username}...")
    User.objects.create_superuser(username, email, password)
    print("Superusuario creado exitosamente.")
else:
    print(f"El usuario {username} ya existe.")
