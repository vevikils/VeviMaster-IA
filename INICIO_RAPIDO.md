# 🚀 Inicio Rápido - VeviMaster-IA con Análisis Musical

## ✅ La integración está COMPLETA y LISTA para usar

## 📍 URLs Correctas del Servidor

El servidor corre en el puerto **8080** (no 8000):

- **Mastering**: http://127.0.0.1:8080/
- **Análisis Musical**: http://127.0.0.1:8080/analyzer/
- **Admin**: http://127.0.0.1:8080/admin/

## 🎯 Iniciar el Servidor (Método Recomendado)

Abre PowerShell en el directorio del proyecto y ejecuta:

```powershell
cd "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA"
.\start_server.ps1
```

## 🎯 Iniciar el Servidor (Método Manual)

Si prefieres hacerlo manualmente:

```powershell
# 1. Ir al directorio del proyecto
cd "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA"

# 2. Activar el entorno virtual de Python 3.11
.\.venv311\Scripts\Activate.ps1

# 3. Ir al directorio de Django
cd vevi_mastering

# 4. Iniciar el servidor en el puerto 8080
python manage.py runserver 8080
```

## 🎵 Funcionalidades Disponibles

### 1. Mastering de Audio
- Accede a: http://127.0.0.1:8080/
- Sube archivos de audio para masterizar

### 2. Análisis Musical con IA
- Accede a: http://127.0.0.1:8080/analyzer/
- Sube un archivo de audio (MP3, WAV, OGG, M4A)
- Obtén análisis de:
  - **24 géneros musicales** con porcentajes
  - **8 estados de ánimo** (happy, sad, energetic, etc.)
  - Visualización con gráficos
  - Historial de análisis

### 3. Panel de Administración
- Accede a: http://127.0.0.1:8080/admin/
- (Necesitas crear un superusuario primero)

## 👤 Crear Superusuario (Opcional)

Para acceder al panel de administración:

```powershell
# Asegúrate de estar en el directorio vevi_mastering con el entorno activado
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador.

## 🔧 Si Necesitas Reinstalar

Si algo no funciona, ejecuta el script de configuración:

```powershell
cd "c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA"
.\setup_python311.ps1
```

Este script:
- Crea el entorno virtual de Python 3.11
- Instala todas las dependencias (Django, TensorFlow, musicnn, etc.)
- Ejecuta las migraciones de la base de datos

## ⚠️ Importante

- **Usa el puerto 8080**, no el 8000
- **Python 3.11 es obligatorio** (TensorFlow no funciona con Python 3.13)
- **El entorno virtual debe estar activado** antes de ejecutar comandos de Django

## 📝 Detener el Servidor

Presiona `Ctrl+C` en la terminal donde está corriendo el servidor.

## 🆘 Solución de Problemas

### Error: "No se puede acceder a este sitio web"
- Verifica que el servidor esté corriendo
- Usa el puerto correcto: **8080** (no 8000)
- URL correcta: http://127.0.0.1:8080/

### Error: "No module named 'tensorflow'"
- Activa el entorno virtual: `.\.venv311\Scripts\Activate.ps1`
- Si persiste, ejecuta: `.\setup_python311.ps1`

### Error: "You don't have permission to access that port"
- Usa el puerto 8080 en lugar de 8000
- Comando: `python manage.py runserver 8080`

## 📚 Documentación Completa

- `INTEGRACION_COMPLETADA.md` - Resumen de la integración
- `INTEGRACION_ANALISIS_MUSICA.md` - Documentación técnica detallada
- `vevi_mastering/analisismusica/README.md` - README original del análisis

---

**¡Listo para usar!** 🎉

Ejecuta `.\start_server.ps1` y accede a http://127.0.0.1:8080/
