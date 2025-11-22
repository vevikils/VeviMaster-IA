#!/bin/bash

# Script de build para Render
echo "Instalando dependencias del sistema..."

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias del sistema para phaselimiter
echo "Instalando librerías necesarias para phaselimiter..."
apt-get update
apt-get install -y libtbb2 libsndfile1 libboost-all-dev unzip

echo "Build completado!"
