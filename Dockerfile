# dockerfile

FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente para instalação não interativa
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
# Garante ffmpeg (necessário para yt-dlp, whisper e conversões)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    ocrmypdf \
    libreoffice \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar diretórios
RUN mkdir -p /app/pages /app/modules

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
# Adicionado --upgrade pip antes de instalar
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos
COPY *.py .
COPY pages/*.py ./pages/
COPY modules/*.py ./modules/
COPY .env* ./

# Porta
EXPOSE 8501

# Define ambiente de execução
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# Comando
CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]
