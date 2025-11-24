# Instrucciones para instalar Python 3.11

## Opción 1: Descargar e instalar Python 3.11 manualmente

1. **Descargar Python 3.11:**
   - Ve a: https://www.python.org/downloads/release/python-31111/
   - Descarga "Windows installer (64-bit)" (o 32-bit si tu sistema es de 32 bits)

2. **Instalar Python 3.11:**
   - Ejecuta el instalador descargado
   - **IMPORTANTE:** Marca la casilla "Add Python 3.11 to PATH"
   - Haz clic en "Install Now"

3. **Verificar la instalación:**
   ```powershell
   python3.11 --version
   ```

4. **Crear un entorno virtual con Python 3.11:**
   ```powershell
   python3.11 -m venv .venv311
   .\.venv311\Scripts\Activate.ps1
   ```

5. **Instalar las dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Ejecutar el programa:**
   ```powershell
   python analyze.py --audio "ruta/al/archivo.mp3"
   ```

## Opción 2: Usar pyenv-win (gestor de versiones de Python)

1. **Instalar pyenv-win:**
   ```powershell
   git clone https://github.com/pyenv-win/pyenv-win.git $HOME\.pyenv
   ```

2. **Configurar variables de entorno** (ver documentación de pyenv-win)

3. **Instalar Python 3.11:**
   ```powershell
   pyenv install 3.11.11
   pyenv local 3.11.11
   ```

## Nota importante

Después de instalar Python 3.11, asegúrate de usar esa versión específica para este proyecto, ya que Python 3.13 tiene problemas de compatibilidad con las dependencias requeridas.

