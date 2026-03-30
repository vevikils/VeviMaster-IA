# Interfaz Web - Analizador de Música

Interfaz web en Django para analizar archivos de audio y detectar géneros musicales y estados de ánimo.

## Características

- ✅ Interfaz web moderna y responsive
- ✅ Carga de archivos por drag & drop o selección
- ✅ Análisis en tiempo real de géneros musicales (20 géneros)
- ✅ Detección de estado de ánimo
- ✅ Visualización de resultados con gráficos
- ✅ Historial de análisis recientes
- ✅ API JSON para integración

## Instalación

### 1. Asegúrate de tener Python 3.11 instalado

```powershell
python3.11 --version
```

### 2. Activa el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instala las dependencias (si no están instaladas)

```powershell
pip install -r requirements.txt
```

### 4. Ejecuta las migraciones

```powershell
python manage.py migrate
```

### 5. Crea un superusuario (opcional, para acceder al admin)

```powershell
python manage.py createsuperuser
```

## Uso

### Iniciar el servidor de desarrollo

```powershell
python manage.py runserver
```

Luego abre tu navegador en: **http://127.0.0.1:8000/**

### Funcionalidades

1. **Subir archivo de audio**: 
   - Arrastra un archivo al área de carga o haz clic para seleccionar
   - Formatos soportados: MP3, WAV, OGG, M4A (máx. 50 MB)

2. **Ver resultados**:
   - Géneros detectados con porcentajes
   - Estado de ánimo predominante
   - Gráficos visuales de los resultados

3. **Historial**:
   - Ver análisis recientes en la página principal
   - Acceder a resultados anteriores

4. **API JSON**:
   - Accede a `/api/results/<id>/` para obtener resultados en JSON

## Estructura del Proyecto

```
analisismusica/
├── analyzer/              # Aplicación Django
│   ├── models.py         # Modelo AudioAnalysis
│   ├── views.py          # Vistas del análisis
│   ├── forms.py          # Formulario de carga
│   ├── urls.py           # URLs de la app
│   └── templates/        # Templates HTML
├── music_analyzer/       # Configuración del proyecto
│   ├── settings.py       # Configuración Django
│   └── urls.py           # URLs principales
├── media/                # Archivos subidos (audio)
├── analyze.py            # Script original de análisis
└── genres_moods.py       # Mapeo de géneros y moods
```

## Notas

- Los archivos de audio se guardan en `media/audio_files/`
- El análisis puede tardar unos segundos dependiendo del tamaño del archivo
- Se requiere FFmpeg para algunos formatos de audio comprimidos

## Solución de Problemas

### Error al cargar archivos grandes

Aumenta el límite en `settings.py`:
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 MB
```

### Error con TensorFlow

Asegúrate de tener Python 3.11 y todas las dependencias instaladas correctamente.

### Error al analizar audio

Verifica que FFmpeg esté instalado y en el PATH del sistema.

