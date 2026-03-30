# Configuración de Google OAuth

## Credenciales

Para habilitar el inicio de sesión con Google, necesitas configurar las siguientes variables de entorno en tu archivo `.env`:

```bash
GOOGLE_CLIENT_ID=tu-client-id-aqui
GOOGLE_CLIENT_SECRET=tu-client-secret-aqui
```

## Obtener las credenciales

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Ve a "APIs & Services" > "Credentials"
4. Crea credenciales OAuth 2.0
5. Añade estas URIs de redirección autorizadas:
   - `https://vevimaster.com/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/`

## Configuración en el servidor

En el servidor Hetzner, asegúrate de que el archivo `.env` en `/var/www/vevimaster/` contenga:

```bash
GOOGLE_CLIENT_ID=tu-client-id-real
GOOGLE_CLIENT_SECRET=tu-client-secret-real
```

Después de actualizar el `.env`, reinicia el contenedor:

```bash
cd /var/www/vevimaster
docker-compose down
docker-compose up -d
```
