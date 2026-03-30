import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vevi_mastering.settings')
django.setup()

User = get_user_model()
email = 'vevikils556@gmail.com'
password = 'Kikudo740+++'

# Como usamos email como método de autenticación, buscamos por email
if not User.objects.filter(email=email).exists():
    print(f"Creando superusuario {email}...")
    User.objects.create_superuser(username=email, email=email, password=password)
    print("Superusuario creado exitosamente.")
else:
    print(f"El usuario {email} ya existe.")
