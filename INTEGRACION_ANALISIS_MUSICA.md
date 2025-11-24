# Integración del Análisis de Música con IA

## ✅ Cambios Realizados

Se ha integrado exitosamente la funcionalidad de análisis de música con IA en el proyecto VeviMaster-IA.

### Archivos Movidos y Creados:

1. **App Django `analyzer`**: Copiada desde `analisismusica/analyzer` a `vevi_mastering/analyzer`
2. **Módulo `genres_moods.py`**: Copiado a `vevi_mastering/genres_moods.py`
3. **Carpeta original**: Movida de `C:\analisismusica` a `VeviMaster-IA\vevi_mastering\analisismusica`

### Configuraciones Actualizadas:

#### 1. `settings.py`
- ✅ Añadida app `'analyzer'` a `INSTALLED_APPS`
- ✅ Configurado `MEDIA_URL = 'media/'`
- ✅ Configurado `MEDIA_ROOT = BASE_DIR / 'media'`
- ✅ Límites de carga de archivos: 50 MB

#### 2. `urls.py`
- ✅ Añadida ruta `path('analyzer/', include('analyzer.urls'))`
- ✅ Configurado servicio de archivos media en desarrollo

#### 3. `requirements.txt`
- ✅ Añadidas dependencias:
  - `musicnn==0.1.0`
  - `numpy>=1.19.0,<1.25`
  - `scipy>=1.2.0`
  - `librosa>=0.7.0`
  - `soundfile>=0.10.0`
  - `tensorflow>=2.5,<2.16`
  - `colorama>=0.4`

#### 4. `analyzer/views.py`
- ✅ Corregidas rutas de importación para el nuevo proyecto

## ⚠️ Requisito Importante: Python 3.11

**IMPORTANTE**: TensorFlow 2.15 requiere Python 3.11 (no es compatible con Python 3.13).

### Opciones de Configuración:

#### Opción 1: Usar el entorno virtual existente (Recomendado para desarrollo local)

El entorno virtual de Python 3.11 ya existe en:
```
VeviMaster-IA\vevi_mastering\analisismusica\.venv
```

Para activarlo:
```powershell
& "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA\vevi_mastering\analisismusica\.venv\Scripts\Activate.ps1"
```

#### Opción 2: Crear un nuevo entorno virtual con Python 3.11

Si tienes Python 3.11 instalado en el sistema:
```powershell
# Navegar al directorio del proyecto
cd "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA"

# Crear entorno virtual con Python 3.11
python3.11 -m venv .venv311

# Activar el entorno
.\.venv311\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

#### Opción 3: Docker (Recomendado para producción)

El Dockerfile ya está configurado. Solo necesitas actualizar la imagen base para usar Python 3.11:

```dockerfile
FROM python:3.11-slim
```

## 📋 Próximos Pasos

### 1. Configurar el Entorno

Activa el entorno virtual de Python 3.11:
```powershell
& "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA\vevi_mastering\analisismusica\.venv\Scripts\Activate.ps1"
```

### 2. Instalar Dependencias (si es necesario)

```powershell
cd "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA\vevi_mastering"
pip install -r ../requirements.txt
```

### 3. Ejecutar Migraciones

```powershell
python manage.py makemigrations analyzer
python manage.py migrate
```

### 4. Crear Superusuario (opcional)

```powershell
python manage.py createsuperuser
```

### 5. Iniciar el Servidor

```powershell
python manage.py runserver
```

## 🎵 Uso de la Funcionalidad

### Interfaz Web

Una vez que el servidor esté corriendo, accede a:

- **Análisis de música**: http://127.0.0.1:8000/analyzer/
- **Mastering**: http://127.0.0.1:8000/

### API JSON

Para obtener resultados en formato JSON:
```
GET /analyzer/api/results/<analysis_id>/
```

## 🔧 Características Integradas

### Análisis de Audio con IA

- ✅ Detección de 24+ géneros musicales
- ✅ Análisis de estado de ánimo (happy, sad, energetic, etc.)
- ✅ Interfaz web con drag & drop
- ✅ Historial de análisis
- ✅ Visualización de resultados con gráficos
- ✅ API REST para integración

### Géneros Detectados

pop, rock, hip hop, electronic, classical, jazz, metal, blues, country, reggae, folk, r&b, soul, funk, house, techno, ambient, latin, punk, disco, trap, drill, hyperpop, reggaeton

### Estados de Ánimo

happy, sad, angry, relaxed, energetic, melancholic, romantic, aggressive

## 📁 Estructura del Proyecto

```
VeviMaster-IA/
├── vevi_mastering/
│   ├── analyzer/              # App de análisis de música
│   │   ├── migrations/
│   │   ├── templates/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   ├── mastering/             # App de mastering
│   ├── vevi_mastering/        # Configuración del proyecto
│   ├── genres_moods.py        # Mapeo de géneros y estados de ánimo
│   ├── media/                 # Archivos subidos (se crea automáticamente)
│   └── analisismusica/        # Proyecto original (referencia)
└── requirements.txt
```

## 🐳 Actualización del Dockerfile

Para usar en producción con Docker, actualiza el Dockerfile:

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY VeviMaster-IA/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VeviMaster-IA/ .

WORKDIR /app/vevi_mastering

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "vevi_mastering.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🚀 Despliegue en Hetzner

El proyecto ya está configurado para desplegarse en Hetzner. Solo asegúrate de:

1. Usar Python 3.11 en el contenedor Docker
2. Instalar FFmpeg en el contenedor
3. Configurar volúmenes para `media/` y `staticfiles/`

## 📝 Notas Adicionales

- Los archivos de audio se guardan en `media/audio_files/`
- El modelo de IA (`musicnn`) se descarga automáticamente en el primer uso
- Los análisis se guardan en la base de datos SQLite (o PostgreSQL en producción)
- El tamaño máximo de archivo es 50 MB (configurable en settings.py)

## ⚡ Solución de Problemas

### Error: "No module named 'tensorflow.python'"

**Causa**: Estás usando Python 3.13, que no es compatible con TensorFlow 2.15.

**Solución**: Usa Python 3.11 (ver sección "Requisito Importante" arriba).

### Error: "FFmpeg not found"

**Solución**: Instala FFmpeg:
- Windows: Descarga desde https://ffmpeg.org/ y añade al PATH
- Linux/Docker: `apt-get install ffmpeg`

### Error al subir archivos grandes

**Solución**: Aumenta los límites en `settings.py`:
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 MB
```
