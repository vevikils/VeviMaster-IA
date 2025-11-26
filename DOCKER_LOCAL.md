# 🐳 Guía de Docker Local - Windows

Esta guía te ayudará a ejecutar **VeviMaster-IA** en tu máquina Windows usando Docker.

## ✅ Prerrequisitos

- ✓ Docker Desktop instalado y corriendo
- ✓ Al menos 4GB de RAM disponible
- ✓ 5GB de espacio en disco

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

Ejecuta el script de PowerShell que configurará todo automáticamente:

```powershell
.\setup_docker_local.ps1
```

El script hará:
1. ✓ Verificar que Docker esté instalado y corriendo
2. ✓ Crear el archivo `.env` con la configuración local
3. ✓ Construir la imagen Docker
4. ✓ Iniciar el contenedor
5. ✓ Ejecutar migraciones de Django
6. ✓ Recolectar archivos estáticos
7. ✓ Abrir la aplicación en tu navegador

### Opción 2: Manual

Si prefieres hacerlo manualmente:

#### 1. Crear archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto con este contenido:

```env
DEBUG=False
SECRET_KEY=b%09d6c$71&cb8h3^tjwe5f0f1y6km5y^ttfp*9sz=6d4n6xb(
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

#### 2. Construir la imagen Docker

```powershell
docker-compose build
```

⏱️ **Nota**: La primera vez puede tardar 5-10 minutos porque descarga:
- Ubuntu 22.04
- Python 3.11
- FFmpeg
- Todas las dependencias de Python
- Los archivos de PhaseLimiter desde Google Drive

#### 3. Iniciar el contenedor

```powershell
docker-compose up -d
```

#### 4. Ejecutar migraciones

```powershell
docker-compose exec web python manage.py migrate
```

#### 5. Recolectar archivos estáticos

```powershell
docker-compose exec web python manage.py collectstatic --noinput
```

#### 6. Acceder a la aplicación

Abre tu navegador en:
```
http://localhost:8000
```

## 🔧 Comandos Útiles

### Ver logs en tiempo real
```powershell
docker-compose logs -f
```

### Ver logs solo del servicio web
```powershell
docker-compose logs -f web
```

### Ver estado de los contenedores
```powershell
docker-compose ps
```

### Reiniciar la aplicación
```powershell
docker-compose restart
```

### Detener la aplicación
```powershell
docker-compose down
```

### Detener y eliminar volúmenes (limpieza completa)
```powershell
docker-compose down -v
```

### Reconstruir la imagen (después de cambios en código)
```powershell
docker-compose build --no-cache
docker-compose up -d
```

### Ejecutar comandos de Django

#### Crear superusuario
```powershell
docker-compose exec web python manage.py createsuperuser
```

#### Abrir shell de Django
```powershell
docker-compose exec web python manage.py shell
```

#### Acceder al contenedor (bash)
```powershell
docker-compose exec web bash
```

## 🐛 Solución de Problemas

### El contenedor no inicia

**Ver los logs:**
```powershell
docker-compose logs web
```

**Verificar que Docker esté corriendo:**
```powershell
docker ps
```

### Error de permisos en PhaseLimiter

Si ves errores relacionados con permisos del binario `phaselimiter`:

```powershell
docker-compose exec web chmod +x /app/vevi_mastering/app_files/phaselimiter/phaselimiter/bin/*
docker-compose restart
```

### Puerto 8000 ya en uso

Si el puerto 8000 está ocupado, puedes cambiarlo editando `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Cambia 8080 por el puerto que prefieras
```

Luego reinicia:
```powershell
docker-compose down
docker-compose up -d
```

### Problemas con la base de datos

Si necesitas resetear la base de datos:

```powershell
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Error al descargar app_files desde Google Drive

Si falla la descarga durante el build, verifica:
1. Que tengas conexión a internet
2. Que el ID de Google Drive sea correcto en el `Dockerfile`

Puedes reconstruir con:
```powershell
docker-compose build --no-cache
```

## 📊 Monitoreo

### Ver uso de recursos
```powershell
docker stats
```

### Ver espacio usado por Docker
```powershell
docker system df
```

### Limpiar recursos no usados
```powershell
docker system prune -a
```

## 🔄 Actualizar la Aplicación

Si haces cambios en el código:

1. **Solo cambios en Python (sin nuevas dependencias):**
   ```powershell
   docker-compose restart
   ```

2. **Cambios en `requirements.txt` o `Dockerfile`:**
   ```powershell
   docker-compose build
   docker-compose up -d
   ```

3. **Cambios en modelos de Django:**
   ```powershell
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

## 🌐 Acceder desde otros dispositivos en tu red local

1. Encuentra tu IP local:
   ```powershell
   ipconfig
   ```
   Busca "Dirección IPv4" (ej: 192.168.1.100)

2. Actualiza el archivo `.env`:
   ```env
   ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
   ```

3. Reinicia:
   ```powershell
   docker-compose restart
   ```

4. Accede desde otro dispositivo:
   ```
   http://192.168.1.100:8000
   ```

## 📝 Notas Importantes

- **Volúmenes persistentes**: Los archivos media y estáticos se guardan en volúmenes Docker, por lo que persisten aunque detengas el contenedor.
- **Base de datos**: Por defecto usa SQLite dentro del contenedor. Los datos se pierden si eliminas el volumen.
- **Performance**: Docker en Windows usa WSL2, puede ser un poco más lento que en Linux nativo.
- **Archivos grandes**: Los archivos de audio procesados se guardan en el volumen `media_files`.

## ✅ Verificación

Para verificar que todo funciona correctamente:

1. ✓ El contenedor está corriendo: `docker-compose ps`
2. ✓ No hay errores en los logs: `docker-compose logs web`
3. ✓ La aplicación responde: Abre `http://localhost:8000`
4. ✓ Puedes subir y procesar un archivo de audio

## 🎯 Siguiente Paso

Una vez que hayas probado la aplicación localmente y todo funcione correctamente, puedes proceder con el despliegue en Hetzner siguiendo la guía `DEPLOY_HETZNER.md`.
