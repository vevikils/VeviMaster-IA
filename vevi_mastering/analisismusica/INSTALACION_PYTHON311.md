# Instalación de Python 3.11 para el proyecto

## Paso 1: Descargar Python 3.11

1. Ve a: https://www.python.org/downloads/release/python-31111/
2. Descarga "Windows installer (64-bit)" para Windows
3. Ejecuta el instalador

## Paso 2: Durante la instalación

**IMPORTANTE**: Marca la casilla "Add Python 3.11 to PATH" antes de hacer clic en "Install Now"

## Paso 3: Verificar la instalación

Abre una nueva terminal PowerShell y ejecuta:
```powershell
python3.11 --version
```

Debería mostrar: `Python 3.11.11`

## Paso 4: Crear entorno virtual con Python 3.11

En la carpeta del proyecto, ejecuta:
```powershell
python3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Paso 5: Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Paso 6: Ejecutar el programa

```powershell
python analyze.py --audio "ruta/al/archivo.mp3"
```


