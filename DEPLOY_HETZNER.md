# Guía de Despliegue en Hetzner con Docker

## 🚀 Pasos para desplegar

### 1. Crear servidor en Hetzner

1. Ve a https://www.hetzner.com/cloud
2. Crea una cuenta si no tienes
3. Crea un nuevo proyecto
4. Crea un servidor (Cloud Server):
   - **Ubicación**: Nuremberg, Germany (o la más cercana)
   - **Imagen**: Ubuntu 22.04
   - **Tipo**: CX11 (2GB RAM, ~€4/mes) o superior
   - **SSH Key**: Agrega tu clave SSH pública
5. Espera a que el servidor se cree (~1 minuto)
6. Anota la IP pública del servidor

### 2. Conectar al servidor

Desde tu terminal local:

```bash
ssh root@TU_IP_DEL_SERVIDOR
```

### 3. Ejecutar script de despliegue

En el servidor, ejecuta:

```bash
# Descargar el script de despliegue
curl -O https://raw.githubusercontent.com/vevikils/VeviMaster-IA/main/deploy-hetzner.sh

# Dar permisos de ejecución
chmod +x deploy-hetzner.sh

# Ejecutar
./deploy-hetzner.sh
```

El script te pedirá que configures las variables de entorno. Edita el archivo `.env`:

```bash
nano .env
```

Configura:
- `SECRET_KEY`: Genera una en https://djecrety.ir/
- `ALLOWED_HOSTS`: Pon la IP de tu servidor (ej: `123.45.67.89`)

Guarda con `Ctrl+O`, Enter, `Ctrl+X`

### 4. Acceder a tu aplicación

Abre en tu navegador:
```
http://TU_IP_DEL_SERVIDOR:8000
```

## 🔧 Comandos útiles

### Ver logs en tiempo real
```bash
cd VeviMaster-IA
docker-compose logs -f
```

### Reiniciar la aplicación
```bash
docker-compose restart
```

### Detener la aplicación
```bash
docker-compose down
```

### Actualizar código desde GitHub
```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### Ejecutar comandos de Django
```bash
# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Ejecutar migraciones
docker-compose exec web python manage.py migrate
```

## 🌐 Configurar dominio (Opcional)

### 1. Apuntar tu dominio a la IP del servidor

En tu proveedor de dominios, crea un registro A:
```
@ -> TU_IP_DEL_SERVIDOR
www -> TU_IP_DEL_SERVIDOR
```

### 2. Instalar Nginx como proxy inverso

```bash
sudo apt-get install nginx certbot python3-certbot-nginx -y
```

### 3. Configurar Nginx

Crea el archivo de configuración:

```bash
sudo nano /etc/nginx/sites-available/vevimaster
```

Pega esta configuración (reemplaza `tu-dominio.com`):

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout para procesamiento de audio
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    client_max_body_size 100M;
}
```

Activa la configuración:

```bash
sudo ln -s /etc/nginx/sites-available/vevimaster /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Instalar certificado SSL (HTTPS)

```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

### 5. Actualizar ALLOWED_HOSTS

Edita el archivo `.env`:

```bash
cd ~/VeviMaster-IA
nano .env
```

Cambia `ALLOWED_HOSTS` a:
```
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,TU_IP
```

Reinicia:
```bash
docker-compose restart
```

## 🔒 Seguridad

### Configurar firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Cambiar puerto SSH (Opcional pero recomendado)

```bash
sudo nano /etc/ssh/sshd_config
# Cambia Port 22 a Port 2222
sudo systemctl restart sshd
sudo ufw allow 2222/tcp
```

## 💰 Costos estimados

- **Hetzner CX11**: ~€4/mes (2GB RAM, 20GB SSD)
- **Hetzner CX21**: ~€6/mes (4GB RAM, 40GB SSD) - Recomendado
- **Dominio**: ~€10/año (opcional)

## 📊 Monitoreo

### Ver uso de recursos

```bash
docker stats
```

### Ver espacio en disco

```bash
df -h
```

### Ver logs de errores

```bash
docker-compose logs --tail=100 web
```

## 🆘 Solución de problemas

### La aplicación no arranca

```bash
# Ver logs
docker-compose logs web

# Verificar que el contenedor esté corriendo
docker-compose ps
```

### Error de permisos

```bash
# Dar permisos a los binarios
docker-compose exec web chmod +x /app/vevi_mastering/app_files/phaselimiter/phaselimiter/bin/*
```

### Actualizar app_files

Si necesitas actualizar el archivo de Google Drive:

1. Edita el `Dockerfile` con el nuevo ID
2. Reconstruye:
```bash
docker-compose build --no-cache
docker-compose up -d
```
