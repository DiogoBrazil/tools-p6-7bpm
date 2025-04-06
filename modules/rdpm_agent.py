import os
import logging
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
# <<< Removido RunnablePassthrough, StrOutputParser, create_retrieval_chain, create_stuff_documents_chain daqui >>>
#     Eles serão usados dentro da função de criação da chain

# <<< Importa TextCorrector aqui para pegar o LLM client dentro da função cacheada >>>
from modules.text_corrector import TextCorrector


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- Constantes ---
PDF_PATH = "files/rdpm.pdf"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
CACHE_DIR = "/app/.cache/huggingface"

# --- Funções Auxiliares ---

# 1. Cache para carregar e indexar o PDF -> Retorna o RETRIEVER
@st.cache_resource(show_spinner=False)
def load_and_get_retriever():
    """Carrega PDF, splita, cria embeddings e retorna o Retriever FAISS."""
    log.info(f"Cache Check: Tentando carregar/indexar PDF: {PDF_PATH}")
    if not os.path.exists(PDF_PATH):
        log.error(f"Arquivo PDF não encontrado em: {PDF_PATH}")
        return None
    try:
        loader = PyPDFLoader(PDF_PATH)
        docs = loader.load()
        if not docs: log.error("..."); return None
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        splits = text_splitter.split_documents(docs)
        if not splits: log.error("..."); return None
        log.info(f"Carregado e dividido em {len(splits)} chunks.")

        log.info(f"Inicializando embeddings: {EMBEDDING_MODEL_NAME}...")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME, cache_folder=CACHE_DIR, model_kwargs={'device': 'cpu'}
        )
        log.info("Embeddings inicializados.")

        log.info("Criando índice FAISS e retriever...")
        vector_index = FAISS.from_documents(splits, embeddings)
        retriever = vector_index.as_retriever(search_type="similarity", search_kwargs={'k': 5})
        log.info("Retriever criado com sucesso a partir do índice FAISS.")
        return retriever
    except Exception as e:
        log.error(f"Erro em load_and_get_retriever: {e}", exc_info=True)
        return None

# 2. Cache para obter o cliente LLM (pode ser útil se TextCorrector fizer algo pesado na inicialização)
@st.cache_resource(show_spinner=False)
def get_llm_client_cached():
    """Obtém o cliente LLM configurado."""
    log.info("Cache Check: Tentando obter LLM client...")
    corrector = TextCorrector()
    client = corrector.get_llm_client()
    if client:
        log.info("LLM client obtido.")
        return client
    else:
        log.error("Falha ao obter LLM client (API não configurada?).")
        return None

# 3. Cache para criar a RAG CHAIN COMPLETA
@st.cache_resource(show_spinner=False)
def get_rag_chain():
    """
    Cria e retorna a cadeia RAG completa, usando componentes cacheados.
    Retorna None se algum componente falhar.
    """
    log.info("Cache Check: Tentando criar/obter RAG chain...")
    # Importa as funções de chain aqui dentro para evitar ciclos se necessário
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain

    # Obtém componentes cacheados
    retriever = load_and_get_retriever()
    llm_client = get_llm_client_cached()

    if not retriever:
        log.error("Falha ao criar RAG chain: Retriever não está disponível.")
        st.error("Erro ao carregar o índice do RDPM.") # Mensagem para o usuário
        return None
    if not llm_client:
        log.error("Falha ao criar RAG chain: LLM Client não está disponível.")
        st.error("Erro ao configurar a conexão com a API de linguagem.") # Mensagem para o usuário
        return None

    try:
        # Define o modelo LLM Langchain
        llm = ChatOpenAI(
            openai_api_key=llm_client.api_key,
            openai_api_base=str(llm_client.base_url),
            model_name=os.getenv("OPENAI_MODEL_NAME", "deepseek-chat"),
            temperature=0.1, max_tokens=1000
        )

        # Define o template do prompt
        prompt_template = """Você é um assistente especializado e muito preciso sobre o Regulamento Disciplinar da Polícia Militar de Rondônia (RDPM). Sua tarefa é responder à pergunta do usuário baseando-se SOMENTE nos trechos do RDPM fornecidos abaixo como contexto.

        Contexto do RDPM:
        {context}

        Pergunta: {input}

        Instruções IMPORTANTES:
        1. Responda de forma clara e objetiva, utilizando as informações presentes EXCLUSIVAMENTE no contexto.
        2. NÃO invente informações, artigos ou detalhes que não estejam no contexto.
        3. Se a resposta para a pergunta não puder ser encontrada no contexto fornecido, diga explicitamente: "A informação solicitada não foi encontrada nos trechos fornecidos do RDPM."
        4. Não adicione opiniões pessoais ou informações externas ao RDPM.
        5. Seja direto na resposta.

        Resposta:"""
        prompt = ChatPromptTemplate.from_template(prompt_template)

        # Cria as cadeias Langchain
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        log.info("RAG chain criada/recuperada do cache com sucesso.")
        return retrieval_chain

    except Exception as e:
        log.error(f"Erro ao criar a RAG chain: {e}", exc_info=True)
        st.error(f"Erro ao configurar o assistente RDPM: {e}")
        return None
