import streamlit as st
from modules.rdpm_agent import get_rag_chain, PDF_PATH
import time
import logging
import os 

# --- Configuração da Página ---
st.set_page_config(
    page_title="Consulta RDPM - 7ºBPM/P-6",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Estilo CSS ---
st.write("""
<style>
    /* Esconde Sidebar */
    [data-testid="stSidebar"] { display: none !important; }
    /* Ajusta container principal */
    .block-container {
        max-width: 900px; /* Largura para chat */
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* === INÍCIO: Estilos do Botão Voltar (Replicado de 1_Ferramentas_PDF.py) === */
    /* Container Botão Voltar - Assume que será o primeiro elemento após este CSS */
    div.element-container:nth-child(1) {
        margin-top: 1rem !important; /* Garante margem superior */
        margin-bottom: 1.5rem !important; /* Espaço consistente abaixo */
    }
    /* Estilo Botão Voltar */
    div.element-container:nth-child(1) > .stButton > button {
        background-color: #f0f2f6 !important;
        color: #333 !important;
        border: 1px solid #d1d1d1 !important;
        font-weight: normal !important;
        box-shadow: none !important;
        width: auto !important;          /* Largura baseada no conteúdo */
        padding: 0.4rem 0.8rem !important; /* Padding interno */
        display: inline-block !important; /* Comportamento normal */
    }
    div.element-container:nth-child(1) > .stButton > button:hover {
        background-color: #e0e2e6 !important;
        color: #111 !important;
        border-color: #c1c1c1 !important;
        box-shadow: none !important;
    }
     /* Estilo de Foco (Opcional, mas bom para acessibilidade) */
    div.element-container:nth-child(1) > .stButton > button:focus {
        box-shadow: 0 0 0 0.2rem rgba(211, 211, 211, 0.5) !important; /* Outline cinza claro */
        outline: none; /* Remove outline padrão do browser se houver */
    }
    /* === FIM: Estilos do Botão Voltar === */

    /* Título e Caption */
    h1 { text-align: center; margin-bottom: 0.5rem; font-size: 1.8rem;}
    /* Target caption mais especifico para evitar conflitos */
    .stApp > .main .block-container > div:nth-child(1) > div > div > div > p.stCaption {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* Estilos minimos para mensagens e expander, confiando nos defaults */
    div[data-testid="stChatMessage"] {
         margin-bottom: 0.8rem;
     }
    div[data-testid="stExpander"] summary {
         font-size: 0.9em; font-weight: 500;
     }
     div[data-testid="stExpander"] div[data-testid="stCaption"] {
         font-size: 0.8em;
     }
     div[data-testid="stExpander"] blockquote {
        border-left: 3px solid #ccc; padding-left: 0.8rem; margin-left: 0; font-style: italic; color: #555;
     }
     div[data-testid="stExpander"] hr { margin: 0.5rem 0; }

    /* Input de Chat */
     div[data-testid="stChatInput"] {
         margin-top: 1rem;
     }
</style>
""", unsafe_allow_html=True)

# --- Botão Voltar ---
# A estilização agora vem do CSS principal acima, usando :nth-child(1)
if st.button("← Voltar à página inicial", key="back_button_rdpm", type='primary'):
    st.switch_page("Home.py")

# --- Título e Caption ---
st.title("⚖️ Consulta ao RDPM/RO")
st.caption("Assistente para tirar dúvidas sobre o Regulamento Disciplinar da Polícia Militar de Rondônia")


# --- Inicialização da RAG Chain ---
rag_chain = None
initialization_placeholder = st.empty()

with initialization_placeholder:
    with st.spinner("Preparando assistente RDPM..."):
        rag_chain = get_rag_chain()

if rag_chain is None:
    initialization_placeholder.error("Falha ao inicializar o assistente RDPM.")
    logging.error("Assistente RDPM não pôde ser inicializado.")
    st.stop()
else:
    initialization_placeholder.empty()
    logging.info("Assistente RDPM pronto para uso.")

    # --- Interface de Chat ---
    if "rdpm_messages" not in st.session_state:
        st.session_state.rdpm_messages = [{"role": "assistant", "content": "Olá! Em que posso ajudar sobre o RDPM/RO?"}]

    # <<< Container para o Chat com Scroll >>>
    chat_container = st.container(height=500)

    with chat_container:
        for idx, message in enumerate(st.session_state.rdpm_messages):
            avatar_icon = "👤" if message["role"] == "user" else "⚖️"
            with st.chat_message(message["role"], avatar=avatar_icon):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "context" in message and message["context"]:
                    with st.expander("🔍 Ver trechos do RDPM utilizados", expanded=False):
                        # ... (código do expander inalterado) ...
                        for i, doc in enumerate(message["context"]):
                            page_num = doc.metadata.get('page', 'N/A')
                            page_content_preview = doc.page_content.strip()[:300] + ("..." if len(doc.page_content.strip()) > 300 else "")
                            display_page = page_num + 1 if isinstance(page_num, int) else 'N/A'
                            st.caption(f"Página: {display_page}")
                            st.markdown(f"> _{page_content_preview}_")
                            if i < len(message["context"]) - 1: st.markdown("---")


    # <<< Chat Input FORA do container de scroll >>>
    if prompt := st.chat_input("Faça sua pergunta sobre o RDPM..."):
        st.session_state.rdpm_messages.append({"role": "user", "content": prompt})
        with st.spinner("Buscando e gerando resposta..."):
            answer = "Ocorreu um erro."
            retrieved_docs = []
            try:
                response = rag_chain.invoke({"input": prompt})
                answer = response.get("answer", "Não consegui encontrar uma resposta relevante.")
                retrieved_docs = response.get("context", [])
                logging.info(f"RAG response generated for prompt: {prompt[:50]}...")
            except Exception as e:
                logging.error(f"Erro RAG chain: {e}", exc_info=True)
                answer = f"Desculpe, ocorreu um erro técnico."
            st.session_state.rdpm_messages.append({
                "role": "assistant",
                "content": answer,
                "context": retrieved_docs
            })
            st.rerun()