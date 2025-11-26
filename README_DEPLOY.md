# 🎵 VeviMaster-IA - Guía Completa de Despliegue

Bienvenido a **VeviMaster-IA**, una aplicación Django para análisis y procesamiento de audio con IA.

## 📚 Índice de Guías

Este proyecto incluye varias guías según tus necesidades:

### 🐳 **DOCKER_LOCAL.md** - Probar localmente con Docker
- ✓ Ejecutar la aplicación en tu máquina Windows con Docker
- ✓ Ideal para desarrollo y pruebas
- ✓ No requiere servidor externo
- 👉 **[Ir a la guía](DOCKER_LOCAL.md)**

### 🌐 **DEPLOY_HETZNER.md** - Desplegar en producción
- ✓ Desplegar en un servidor Hetzner con Docker
- ✓ Aplicación accesible desde internet
- ✓ Costo: ~€4-6/mes
- 👉 **[Ir a la guía](DEPLOY_HETZNER.md)**

### ⚡ **INICIO_RAPIDO.md** - Desarrollo local sin Docker
- ✓ Ejecutar directamente con Python en Windows
- ✓ Para desarrollo y debugging
- ✓ No requiere Docker
- 👉 **[Ir a la guía](INICIO_RAPIDO.md)**

---

## 🚀 Inicio Rápido

### Opción A: Probar Localmente con Docker (Recomendado)

**Requisitos:**
- Docker Desktop instalado y corriendo
- 4GB RAM disponible
- 5GB espacio en disco

**Pasos:**
```powershell
# 1. Ejecutar script de configuración
.\setup_docker_local.ps1

# 2. Esperar a que termine (~5-10 minutos la primera vez)

# 3. Abrir navegador en http://localhost:8000
```

📖 **Guía completa:** [DOCKER_LOCAL.md](DOCKER_LOCAL.md)

---

### Opción B: Desplegar en Hetzner

**Requisitos:**
- Cuenta en Hetzner Cloud
- ~€4-6/mes para el servidor
- Cliente SSH

**Pasos:**

**1. Preparar desde Windows:**
```powershell
.\prepare_hetzner.ps1 -ServerIP TU_IP_DEL_SERVIDOR
```

**2. Conectar al servidor:**
```powershell
ssh root@TU_IP_DEL_SERVIDOR
```

**3. Ejecutar en el servidor:**
```bash
curl -O https://raw.githubusercontent.com/vevikils/VeviMaster-IA/main/deploy-hetzner.sh
chmod +x deploy-hetzner.sh
./deploy-hetzner.sh
```

**4. Acceder:**
```
http://TU_IP_DEL_SERVIDOR:8000
```

📖 **Guía completa:** [DEPLOY_HETZNER.md](DEPLOY_HETZNER.md)

---

### Opción C: Desarrollo Local sin Docker

**Requisitos:**
- Python 3.11
- FFmpeg
- 2GB RAM disponible

**Pasos:**
```powershell
# 1. Configurar Python 3.11
.\setup_python311.ps1

# 2. Iniciar servidor
.\start_server.ps1

# 3. Abrir navegador en http://localhost:8000
```

📖 **Guía completa:** [INICIO_RAPIDO.md](INICIO_RAPIDO.md)

---

## 🛠️ Scripts Disponibles

### Windows (PowerShell)

| Script | Descripción | Uso |
|--------|-------------|-----|
| `setup_docker_local.ps1` | Configurar Docker localmente | `.\setup_docker_local.ps1` |
| `prepare_hetzner.ps1` | Preparar despliegue en Hetzner | `.\prepare_hetzner.ps1 -ServerIP <IP>` |
| `setup_python311.ps1` | Instalar Python 3.11 | `.\setup_python311.ps1` |
| `start_server.ps1` | Iniciar servidor de desarrollo | `.\start_server.ps1` |

### Linux/Servidor (Bash)

| Script | Descripción | Uso |
|--------|-------------|-----|
| `deploy-hetzner.sh` | Desplegar en servidor Hetzner | `./deploy-hetzner.sh` |
| `download_app_files.sh` | Descargar archivos de la app | `./download_app_files.sh` |
| `render-build.sh` | Build para Render.com | `./render-build.sh` |

---

## 📁 Estructura del Proyecto

```
vevi mastering ia django 31-7-25/
├── VeviMaster-IA/              # Código fuente de la aplicación
│   ├── vevi_mastering/         # Proyecto Django
│   │   ├── mastering/          # App principal
│   │   ├── analyzer/           # App de análisis de audio
│   │   └── vevi_mastering/     # Configuración Django
│   ├── requirements.txt        # Dependencias Python
│   └── .env.example            # Ejemplo de configuración
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Orquestación Docker
├── DOCKER_LOCAL.md             # Guía Docker local
├── DEPLOY_HETZNER.md           # Guía despliegue Hetzner
├── INICIO_RAPIDO.md            # Guía desarrollo local
└── README_DEPLOY.md            # Este archivo
```

---

## 🔧 Comandos Útiles

### Docker Local

```powershell
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Ver estado
docker-compose ps

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

### Docker en Hetzner (SSH)

```bash
# Conectar al servidor
ssh root@TU_IP

# Ver logs
cd VeviMaster-IA
docker-compose logs -f

# Reiniciar
docker-compose restart

# Actualizar código
git pull origin main
docker-compose build
docker-compose up -d
```

### Desarrollo Local

```powershell
# Activar entorno virtual
.\.venv311\Scripts\Activate.ps1

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

---

## 🐛 Solución de Problemas Comunes

### Docker no inicia

**Problema:** `docker: command not found` o error al conectar

**Solución:**
1. Verifica que Docker Desktop esté corriendo
2. Reinicia Docker Desktop
3. Verifica con: `docker --version`

### Puerto 8000 ocupado

**Problema:** `Error: port is already allocated`

**Solución:**
```powershell
# Opción 1: Detener el proceso que usa el puerto
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Opción 2: Cambiar puerto en docker-compose.yml
# Edita: ports: - "8080:8000"
```

### Error al descargar app_files

**Problema:** Falla la descarga desde Google Drive durante el build

**Solución:**
```powershell
# Reconstruir sin caché
docker-compose build --no-cache
```

### Problemas de permisos en Linux

**Problema:** `Permission denied` al ejecutar phaselimiter

**Solución:**
```bash
docker-compose exec web chmod +x /app/vevi_mastering/app_files/phaselimiter/phaselimiter/bin/*
docker-compose restart
```

---

## 📊 Comparación de Opciones

| Característica | Docker Local | Hetzner | Desarrollo Local |
|----------------|--------------|---------|------------------|
| **Costo** | Gratis | ~€4-6/mes | Gratis |
| **Acceso Internet** | No | Sí | No |
| **Configuración** | Media | Media | Fácil |
| **Tiempo Setup** | 10-15 min | 15-20 min | 5-10 min |
| **Ideal para** | Pruebas | Producción | Desarrollo |
| **Requisitos** | Docker | Servidor | Python 3.11 |

---

## 🎯 Recomendaciones

### Para Desarrollo
1. Usa **Desarrollo Local** (`INICIO_RAPIDO.md`) para debugging rápido
2. Prueba con **Docker Local** (`DOCKER_LOCAL.md`) antes de desplegar

### Para Producción
1. Primero prueba localmente con Docker
2. Luego despliega en **Hetzner** (`DEPLOY_HETZNER.md`)
3. Configura un dominio y SSL (ver guía Hetzner)

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa las guías específicas** según tu caso de uso
2. **Verifica los logs:**
   - Docker: `docker-compose logs -f`
   - Local: Revisa la consola donde ejecutaste el servidor
3. **Problemas comunes:** Revisa la sección "Solución de Problemas" arriba

---

## 📝 Notas Importantes

- **SECRET_KEY**: Nunca compartas tu SECRET_KEY en producción
- **DEBUG**: Siempre debe ser `False` en producción
- **ALLOWED_HOSTS**: Debe incluir tu dominio/IP en producción
- **Backups**: Haz backups regulares de tu base de datos y archivos media
- **Actualizaciones**: Mantén Docker y dependencias actualizadas

---

## ✅ Checklist de Despliegue

### Antes de desplegar en producción:

- [ ] Probado localmente con Docker
- [ ] SECRET_KEY generada y segura
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] Archivos estáticos recolectados
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Firewall configurado (si aplica)
- [ ] Backup configurado
- [ ] SSL/HTTPS configurado (recomendado)

---

## 🎉 ¡Listo!

Ahora tienes toda la información necesaria para ejecutar **VeviMaster-IA** en cualquier entorno.

**Siguiente paso:** Elige la opción que mejor se adapte a tus necesidades y sigue la guía correspondiente.

¡Buena suerte! 🚀
