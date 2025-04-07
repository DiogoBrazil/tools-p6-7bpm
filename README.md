# 🛠️ Ferramentas P/6 - 7º BPM

Um portal web desenvolvido com Streamlit e Python, reunindo um conjunto de ferramentas digitais para otimizar processos administrativos na Seção de Justiça e Disciplina (P/6) do 7º Batalhão de Polícia Militar.

## ✨ Funcionalidades

O portal oferece as seguintes ferramentas:

*   **📄 Ferramentas PDF:**
    *   Compressão e Otimização de arquivos PDF (usando Ghostscript).
    *   Reconhecimento Óptico de Caracteres (OCR) para tornar PDFs pesquisáveis (usando OCRmyPDF).
    *   Junção de múltiplos arquivos PDF em um único documento.
    *   Conversão de Imagens (JPG, PNG) para PDF.
    *   Conversão de PDF para DOCX (Word), com opção de aplicar OCR em PDFs baseados em imagem.
    *   Conversão de PDF para Imagens (PNG).
    *   Conversão de Documentos (DOCX, DOC, ODT, TXT) para PDF (usando LibreOffice).
    *   Conversão de Planilhas (XLSX, CSV, ODS) para PDF (usando LibreOffice).
*   **📝 Corretor de Texto:**
    *   Correção gramatical e ortográfica de textos em Português Brasileiro utilizando LLM (configurável via API - ex: DeepSeek, OpenAI).
    *   Refinamento específico para transcrições de áudio.
*   **🎵 Conversor Vídeo para MP3:**
    *   Extração rápida de áudio de diversos formatos de vídeo (MP4, AVI, MOV, etc.) para o formato MP3 (usando FFmpeg).
*   **🎤 Transcritor de Áudio:**
    *   Transcrição de arquivos de áudio (MP3, WAV, M4A, etc.) para texto utilizando o modelo Whisper da OpenAI.
    *   Opção de refinamento da transcrição bruta utilizando a mesma API LLM do corretor de texto.
*   **⚖️ Consulta ao RDPM:**
    *   Chatbot baseado em RAG (Retrieval-Augmented Generation) para realizar perguntas e obter respostas sobre o conteúdo do Regulamento Disciplinar da Polícia Militar de Rondônia (RDPM), utilizando um arquivo PDF específico como base de conhecimento.
*   **⏳ Calculadora de Prescrição:**
    *   Cálculo de datas de prescrição para infrações disciplinares, considerando a natureza da infração (Leve, Média, Grave), a data de conhecimento, a data de instauração do procedimento (interrupção) e múltiplos períodos de suspensão.

## 💻 Tecnologias Utilizadas

*   **Linguagem:** Python 3.10+
*   **Framework Web:** Streamlit
*   **Containerização:** Docker, Docker Compose
*   **Proxy Reverso & HTTPS:** Traefik, Let's Encrypt
*   **Processamento PDF:** PyMuPDF, PyPDF2, Ghostscript, OCRmyPDF, LibreOffice, img2pdf, Pillow
*   **Processamento de Mídia:** FFmpeg, openai-whisper
*   **IA & NLP:** Langchain, FAISS, Sentence Transformers, API OpenAI/DeepSeek (via `openai` SDK)
*   **Outros:** python-docx, python-dateutil, Pandas, python-dotenv

## ⚙️ Pré-requisitos

*   Docker Engine: [Instruções de instalação](https://docs.docker.com/engine/install/)
*   Docker Compose: (Geralmente incluído na instalação do Docker Desktop, ou veja [instruções separadas](https://docs.docker.com/compose/install/))
*   Git (para clonar o repositório)
*   Um servidor (VPS ou local) com acesso à internet.
*   **Para deploy com HTTPS:**
    *   Portas 80 e 443 abertas no firewall do servidor.
    *   Um domínio ou subdomínio válido apontado para o endereço IP público do servidor.

## 🔧 Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <url_do_seu_repositorio>
    cd <nome_do_diretorio>
    ```
2.  **Crie o arquivo de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto.
3.  **Configure as variáveis de ambiente no `.env`:**
    Adicione as chaves de API e configurações necessárias. Pelo menos as seguintes são recomendadas para funcionalidade completa:
    ```dotenv
    # Credenciais para o Corretor de Texto e Consulta RDPM (Exemplo DeepSeek)
    # Substitua pelos seus valores reais se usar OpenAI ou outro serviço
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    OPENAI_BASE_URL="https://api.deepseek.com" # Ou https://api.openai.com/v1
    OPENAI_MODEL_NAME="deepseek-chat" # Ou gpt-3.5-turbo, gpt-4, etc.

    # Outras variáveis de ambiente podem ser adicionadas aqui se necessário
    ```
    *Observação:* O email para o Let's Encrypt é configurado diretamente no arquivo `docker-compose.yml`.

## 🚀 Instalação e Execução (Docker - Método Recomendado)

Este método utiliza Docker e Docker Compose para gerenciar o ambiente, as dependências e o deploy, incluindo HTTPS com Traefik.

1.  **Certifique-se** de que os pré-requisitos (Docker, Docker Compose) estão instalados.
2.  **Configure o arquivo `.env`** conforme a seção anterior.
3.  **Prepare para HTTPS (Deploy com Traefik):**
    *   Verifique se o seu domínio/subdomínio (ex: `seu.subdomineo.nexuslearn.com.br`) está apontando corretamente para o IP do seu servidor.
    *   Garanta que as portas `80` e `443` estão abertas no firewall do seu servidor e não estão sendo usadas por outros serviços (exceto pelo Traefik que será iniciado).
    *   **Edite o arquivo `docker-compose.yml`:**
        *   Localize a seção do serviço `traefik`.
        *   Atualize a linha `--certificatesresolvers.myresolver.acme.email=SEU_EMAIL_AQUI@example.com` com seu email real.
        *   Localize a seção `labels` do serviço `ferramentas-app`.
        *   Confirme se a regra `Host(\`ferramentas-p6-7bpm.nexuslearn.com.br\`)` está correta para o seu domínio. Ajuste se necessário.
    *   **Crie o diretório e arquivo para os certificados Let's Encrypt** na raiz do projeto:
        ```bash
        mkdir letsencrypt
        touch letsencrypt/acme.json
        chmod 600 letsencrypt/acme.json # Define permissões restritas
        ```
4.  **Construa e Inicie os Containers:**
    Execute o comando na raiz do projeto:
    ```bash
    docker compose up --build -d
    ```
    *   `--build`: Reconstrói as imagens se houver mudanças (importante na primeira vez ou após alterar `Dockerfile` ou `requirements.txt`).
    *   `-d`: Executa os containers em segundo plano (detached mode).

5.  **Acesse a Aplicação:**
    Após alguns instantes (o Traefik precisa obter o certificado na primeira vez), acesse a aplicação no seu navegador usando HTTPS:
    `https://seu-domíneo.com.br` (substitua pelo seu domínio, se diferente).

6.  **(Opcional) Acessar Dashboard do Traefik:**
    Se habilitado no `docker-compose.yml` (porta 8080), você pode acessar `http://SEU_IP_DO_SERVIDOR:8080` para ver o dashboard do Traefik.

## 🔌 Parando a Aplicação

Para parar os containers, navegue até o diretório raiz do projeto no terminal e execute:

```bash
docker compose down