# Guía de Despliegue en Hetzner con Docker

Esta guía te ayudará a desplegar **VeviMaster-IA** en un servidor Hetzner usando Docker.

## 📋 Requisitos Previos

- ✓ Cuenta en [Hetzner Cloud](https://www.hetzner.com/cloud)
- ✓ Cuenta en [GitHub](https://github.com) (para clonar el repositorio)
- ✓ Cliente SSH instalado en tu máquina local
- ✓ ~€4-6/mes para el servidor

## 🚀 Parte 1: Preparación desde Windows

### Paso 1: Preparar archivos de configuración

Ejecuta el script de preparación en tu máquina Windows:

```powershell
.\prepare_hetzner.ps1 -ServerIP TU_IP_DEL_SERVIDOR
```

Este script:
- ✓ Genera una `SECRET_KEY` segura automáticamente
- ✓ Crea el archivo `.env.hetzner` con la configuración correcta
- ✓ Te ayuda a hacer commit y push de los cambios (opcional)

**Ejemplo:**
```powershell
.\prepare_hetzner.ps1 -ServerIP 95.217.161.141
```

### Paso 2: Verificar configuración

El script creará un archivo `.env.hetzner` que se verá así:

```env
DEBUG=False
SECRET_KEY=tu_secret_key_generada_automaticamente
ALLOWED_HOSTS=95.217.161.141
DATABASE_URL=sqlite:///db.sqlite3
```

**Guarda este contenido**, lo necesitarás en el servidor.

---

## 🌐 Parte 2: Crear Servidor en Hetzner

### Paso 1: Crear cuenta y proyecto

1. Ve a [Hetzner Cloud](https://www.hetzner.com/cloud)
2. Crea una cuenta si no tienes (necesitarás una tarjeta de crédito)
3. Crea un nuevo proyecto (ej: "VeviMaster-IA")

### Paso 2: Crear servidor

1. Haz clic en **"Add Server"**
2. Configura:
   - **Ubicación**: Nuremberg, Germany (o la más cercana a ti)
   - **Imagen**: Ubuntu 22.04
   - **Tipo**: 
     - **CX21** (4GB RAM, 40GB SSD) - **Recomendado** (~€6/mes)
     - CX11 (2GB RAM, 20GB SSD) - Mínimo (~€4/mes)
   - **Networking**: IPv4 (por defecto)
   - **SSH Keys**: 
     - Si tienes una clave SSH, agrégala aquí
     - Si no, puedes usar contraseña (menos seguro)
   - **Nombre**: vevi-master-ia

3. Haz clic en **"Create & Buy now"**
4. Espera ~1 minuto a que el servidor se cree
5. **Anota la IP pública** que aparece (ej: `95.217.161.141`)

### Paso 3: Conectar al servidor

Desde PowerShell o CMD en Windows:

```powershell
ssh root@TU_IP_DEL_SERVIDOR
```

**Ejemplo:**
```powershell
ssh root@95.217.161.141
```

Si es la primera vez, te preguntará si confías en el servidor, escribe `yes`.

---

## 🐳 Parte 3: Desplegar en el Servidor

### Paso 1: Ejecutar script de despliegue

Una vez conectado al servidor vía SSH, ejecuta:

```bash
# Descargar el script de despliegue
curl -O https://raw.githubusercontent.com/vevikils/VeviMaster-IA/main/deploy-hetzner.sh

# Dar permisos de ejecución
chmod +x deploy-hetzner.sh

# Ejecutar
./deploy-hetzner.sh
```

### Paso 2: Configurar variables de entorno

El script te pedirá que configures el archivo `.env`. Cuando veas el mensaje:

```
⚠️  IMPORTANTE: Edita el archivo .env con tus valores:
   nano .env
```

Presiona Enter y luego:

```bash
nano .env
```

**Copia el contenido del archivo `.env.hetzner`** que generaste en Windows (Parte 1, Paso 2).

Para pegar en nano:
- En PowerShell/Windows Terminal: Clic derecho
- En PuTTY: Clic derecho

Guarda y cierra:
- `Ctrl+O` (guardar)
- `Enter` (confirmar)
- `Ctrl+X` (salir)

### Paso 3: Continuar con el despliegue

Presiona `Enter` para continuar. El script:
- ✓ Construirá la imagen Docker (~5-10 minutos)
- ✓ Iniciará el contenedor
- ✓ Ejecutará las migraciones de Django
- ✓ Recolectará archivos estáticos

### Paso 4: Acceder a tu aplicación

Una vez completado, verás un mensaje como:

```
✅ Despliegue completado!
Tu aplicación está corriendo en: http://95.217.161.141:8000
```

Abre esa URL en tu navegador. ¡Listo! 🎉

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
