from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Configura Google OAuth para django-allauth'

    def handle(self, *args, **options):
        # Obtener el sitio actual
        site = Site.objects.get_current()
        
        # Credenciales de Google OAuth desde variables de entorno
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_CLIENT_SECRET')

        if not client_id or not secret:
            self.stdout.write(self.style.WARNING('⚠ No se encontraron credenciales de Google OAuth en variables de entorno.'))
            self.stdout.write(self.style.WARNING('  Asegúrate de configurar GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET.'))
            return
        
        # Crear o actualizar la aplicación social de Google
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if not created:
            # Si ya existía, actualizar las credenciales
            google_app.client_id = client_id
            google_app.secret = secret
            google_app.save()
            self.stdout.write(self.style.SUCCESS('✓ Credenciales de Google actualizadas'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Aplicación de Google creada'))
        
        # Asociar con el sitio actual
        if site not in google_app.sites.all():
            google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'✓ Google OAuth asociado al sitio: {site.domain}'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Google OAuth configurado correctamente!'))
        self.stdout.write(self.style.WARNING('\nAsegúrate de que en Google Cloud Console tengas configuradas estas URIs de redirección:'))
        self.stdout.write(f'  - https://{site.domain}/accounts/google/login/callback/')
        self.stdout.write(f'  - http://localhost:8000/accounts/google/login/callback/')
