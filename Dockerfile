COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY VeviMaster-IA/ .

# Descargar app_files desde Google Drive
RUN pip install gdown && \
    gdown "https://drive.google.com/uc?id=1CNe457Xc-m3DB4_W37Poba--IjXvnQ9k" -O app_files.zip && \
    unzip -q app_files.zip -d vevi_mastering/ && \
    rm app_files.zip && \
    chmod +x vevi_mastering/app_files/phaselimiter/phaselimiter/bin/*

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/app/vevi_mastering/app_files/phaselimiter/phaselimiter/bin:$LD_LIBRARY_PATH

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
WORKDIR /app/vevi_mastering
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "300", "vevi_mastering.wsgi:application"]
