FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar Python 3.8, ffmpeg y dependencias del sistema
# IMPORTANTE: Python 3.8 es necesario para compatibilidad con musicnn y numpy<1.17
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.8 \
    python3.8-venv \
    python3.8-dev \
    python3-pip \
    curl \
    unzip \
    libtbb2 \
    libsndfile1 \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Configurar Python 3.8 como predeterminado
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# Asegurar pip actualizado (usar URL específica para Python 3.8)
RUN curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8

WORKDIR /app

# Instalar dependencias de Python
COPY VeviMaster-IA/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY VeviMaster-IA/vevi_mastering ./vevi_mastering

# Descargar y configurar PhaseLimiter
# Nota: chmod +x es CRÍTICO para que el binario funcione en Linux
RUN pip install gdown && \
    gdown "https://drive.google.com/uc?id=1CNe457Xc-m3DB4_W37Poba--IjXvnQ9k" -O app_files.zip && \
    unzip -o -q app_files.zip -d vevi_mastering/ && \
    rm app_files.zip && \
    chmod -R 755 vevi_mastering/app_files/phaselimiter/phaselimiter/bin/

# Configurar variables de entorno para librerías dinámicas si fuera necesario
ENV LD_LIBRARY_PATH=/app/vevi_mastering/app_files/phaselimiter/phaselimiter/bin:$LD_LIBRARY_PATH

EXPOSE 8000

WORKDIR /app/vevi_mastering

# Comando de inicio con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "vevi_mastering.wsgi:application"]
