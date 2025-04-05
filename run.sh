#!/bin/bash

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Construir e iniciar os contêineres
echo "Iniciando a aplicação de compressão de PDF..."
docker compose up --build -d

echo "Aplicação iniciada! Acesse através do navegador:"
echo "http://localhost:8501"