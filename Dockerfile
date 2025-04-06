# tools-p6-7bpm/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente para instalação não interativa
ENV DEBIAN_FRONTEND=noninteractive
# Variáveis para build (podem ser necessárias para faiss ou sentence-transformers)
# ENV CMAKE_ARGS="-DLLAMA_CUBLAS=OFF" # Removido - provavelmente não necessário para FAISS-CPU
# ENV FORCE_CMAKE=1 # Removido - geralmente não necessário

# Instalar dependências do sistema
# Garante build-essential e cmake
RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    ocrmypdf \
    libreoffice \
    ffmpeg \
    libpq-dev \
    build-essential \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar diretórios
RUN mkdir -p /app/pages /app/modules /app/files # Garante que /files exista

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
# A instalação pode demorar um pouco mais agora
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos
COPY *.py .
COPY pages/*.py ./pages/
COPY modules/*.py ./modules/
COPY .env* ./
COPY files/rdpm.pdf ./files/rdpm.pdf

# Porta
EXPOSE 8501

# Define ambiente de execução
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    # <<< MOVIDO PARA ENV: Define cache do HuggingFace/SentenceTransformers >>>
    TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers \
    HF_HOME=/app/.cache/huggingface

# <<< REMOVIDO da seção de instruções RUN >>>
# TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers
# HF_HOME=/app/.cache/huggingface

# Cria diretório de cache e ajusta permissões (opcional, mas bom)
# Executado como root durante o build
RUN mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache

# Comando principal
CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]
