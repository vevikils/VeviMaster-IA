#!/bin/bash

# Script para descargar app_files desde Google Drive
echo "Verificando si app_files existe..."

APP_FILES_DIR="vevi_mastering/app_files"

if [ -d "$APP_FILES_DIR" ]; then
    echo "app_files ya existe, omitiendo descarga..."
else
    echo "Descargando app_files desde Google Drive..."
    
    # Instalar gdown si no está disponible
    pip install gdown
    
    # Descargar el archivo comprimido desde Google Drive
    # REEMPLAZA 'YOUR_GOOGLE_DRIVE_FILE_ID' con el ID real de tu archivo
    gdown "https://drive.google.com/uc?id=1SAm4l3MjK8Rg1PNSgKi_C0WLOEUIf3Or" -O app_files.zip
    
    # Descomprimir
    unzip -q app_files.zip -d vevi_mastering/
    
    # Limpiar archivo zip
    rm app_files.zip
    
    # Dar permisos de ejecución a los binarios
    chmod +x vevi_mastering/app_files/phaselimiter/phaselimiter/bin/*
    
    echo "app_files descargado y configurado correctamente!"
fi
