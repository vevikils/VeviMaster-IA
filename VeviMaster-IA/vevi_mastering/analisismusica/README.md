# Analisis de Música (género y estado de ánimo)

Proyecto en Python que usa un modelo de IA gratuito (`musicnn`) para analizar un archivo de audio, estimar el porcentaje de coincidencia con 20 géneros musicales y detectar el estado de ánimo predominante.

## Requisitos

- **Python 3.11** (requerido - Python 3.13 no es compatible)
- FFmpeg instalado en el sistema (recomendado para mejor soporte de formatos como MP3/MP4)
- Windows: este proyecto está pensado para funcionar en Windows 10/11

## Instalación

### Paso 1: Instalar Python 3.11

Si no tienes Python 3.11 instalado:

1. Descarga Python 3.11 desde: https://www.python.org/downloads/release/python-31111/
2. Ejecuta el instalador y **marca la casilla "Add Python 3.11 to PATH"**
3. Verifica la instalación: `python3.11 --version`

### Paso 2: Configurar el entorno

**Opción A - Script automático (recomendado):**

```powershell
.\setup_python311.ps1
```

**Opción B - Manual:**

1) Crear y activar un entorno virtual con Python 3.11:

```powershell
python3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Si no tienes FFmpeg, descárgalo e instálalo y asegúrate de añadirlo al PATH del sistema.

## Uso

**Importante:** Asegúrate de activar el entorno virtual primero:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Opción 1: Interfaz Web (Recomendado) 🎨

Interfaz web moderna con drag & drop para subir archivos:

```powershell
# Iniciar el servidor
.\start_server.ps1

# O manualmente:
python manage.py runserver
```

Luego abre tu navegador en: **http://127.0.0.1:8000/**

**Características de la interfaz web:**
- ✅ Carga de archivos por drag & drop
- ✅ Visualización de resultados con gráficos
- ✅ Historial de análisis recientes
- ✅ API JSON para integración
- ✅ Interfaz responsive y moderna

Ver [README_WEB.md](README_WEB.md) para más detalles.

### Opción 2: Línea de Comandos

Analizar un archivo de audio y ver resultados legibles:

```powershell
python analyze.py --audio "ruta/al/archivo.mp3"
```

Obtener salida en JSON (útil para integrar en otras apps):

```powershell
python analyze.py --audio "ruta/al/archivo.mp3" --json
```

Salida esperada:
- Porcentaje de coincidencia entre 20 géneros predefinidos
- Estado de ánimo más probable (y puntuación)

## Notas
- El modelo `musicnn` devuelve etiquetas (tags) musicales. Este proyecto mapea esas etiquetas a 20 géneros y a varias categorías de estado de ánimo.
- Los porcentajes se normalizan a 100% sobre los géneros detectados; si el modelo no detecta nada relacionado con los 20 géneros, los porcentajes podrían ser 0.
- Formatos comunes compatibles: WAV, MP3, OGG, M4A (dependiendo del backend de decodificación disponible).

## Licencia
MIT


