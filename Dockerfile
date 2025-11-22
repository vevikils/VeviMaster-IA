FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python, ffmpeg y dependencias
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    curl \
    unzip \
    libtbb2 \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY VeviMaster-IA/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY VeviMaster-IA/vevi_mastering ./vevi_mastering

RUN pip3 install gdown && \
    gdown "https://drive.google.com/uc?id=1CNe457Xc-m3DB4_W37Poba--IjXvnQ9k" -O app_files.zip && \
    unzip -q app_files.zip -d vevi_mastering/ && \
    rm app_files.zip && \
    chmod +x vevi_mastering/app_files/phaselimiter/phaselimiter/bin/* || true

ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/app/vevi_mastering/app_files/phaselimiter/phaselimiter/bin:$LD_LIBRARY_PATH

EXPOSE 8000

WORKDIR /app/vevi_mastering
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "300", "vevi_mastering.wsgi:application"]
