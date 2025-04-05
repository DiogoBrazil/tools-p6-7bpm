# dockerfile

FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente para instalação não interativa
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema (Ghostscript, Tesseract, OCRmyPDF e LibreOffice)
# Usar o meta-pacote 'libreoffice' para garantir a instalação completa
RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    ocrmypdf \
    libreoffice \
    # Remover libreoffice-writer e libreoffice-headless se o meta-pacote for usado
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar diretórios para as páginas e módulos
RUN mkdir -p /app/pages /app/modules

# Copiar arquivos do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY pages/*.py ./pages/
COPY modules/*.py ./modules/
COPY .env* ./

# Porta que o Streamlit vai usar
EXPOSE 8501

# Define ambiente de execução
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]
