# tools-p-7bpm/Home.py
import streamlit as st
import time # Para delay no JS (pode remover se não usar o JS)
# <<< REMOVIDO: from modules.database import initialize_database >>>
import logging # Para logs (opcional)
import os

# --- Configuração da Página (PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(
    page_title="Ferramentas - 7ºBPM/P-6",
    page_icon="🛠️",
    layout="wide", # Layout largo para acomodar cards
    initial_sidebar_state="collapsed"
)

# --- REMOVIDO: Bloco de INICIALIZAÇÃO DO BANCO E VERIFICAÇÃO DE LOGIN ---

# --- REMOVIDO: Bloco de Informações do Usuário e Logout ---


# --- Estilos CSS (Restaurado e Redimensionado) ---
st.markdown("""
<style>
    /* === GERAL === */
    [data-testid="stSidebar"] { display: none !important; } /* Esconde sidebar */
    .block-container { max-width: 100%; padding: 1rem 1.5rem; } /* Padding vertical reduzido */
    .main-header { font-size: 2.1rem; margin-bottom: 0.6rem; text-align: center; color: #333; font-weight: 600; }
    .main-description { font-size: 1.0rem; margin-bottom: 1.5rem; text-align: center; color: #555; line-height: 1.6; }
    .footer { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e6; text-align: center; font-size: 0.85rem; color: #777; }

    /* === CARD (REDIMENSIONADO) === */
    .tool-card { background-color: #ffffff; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.2rem; transition: transform 0.3s ease, box-shadow 0.3s ease; text-align: center; border: 1px solid #e9e9e9; box-shadow: 0 3px 8px rgba(0,0,0,0.05); height: 290px; display: flex; flex-direction: column; justify-content: space-between; }
    .tool-card:hover { transform: translateY(-4px); box-shadow: 0 6px 14px rgba(0,0,0,0.08); }

    /* === CONTEÚDO DO CARD (REDIMENSIONADO) === */
    .tool-icon { font-size: 2.4rem; margin-bottom: 0.4rem; display: block; }
    .tool-title { font-size: 1.2rem; margin-bottom: 0.4rem; color: #2c3e50; font-weight: 600; }
    .tool-card p { margin-bottom: 0.5rem; color: #666; line-height: 1.4; font-size: 0.85rem; }
    .tool-card ul { padding-left: 1rem; margin: 0.2rem 0 0.6rem 0; text-align: left; color: #555; font-size: 0.8rem; }
    .tool-card li { margin-bottom: 0.2rem; }

    /* === BOTÃO GRANDE NO CARD (Primário) === */
    div.tool-card div.stButton > button[data-testid*="stButton-primary"] { /* Target primário dentro do card */
        width: 100%; height: 45px; font-size: 0.95rem; font-weight: bold; transition: all 0.3s ease; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.07); margin-top: auto; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer;
    }
    div.tool-card div.stButton > button[data-testid*="stButton-primary"]:hover {
        transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* Cores específicas dos botões dos cards (Primários) */
    .btn-pdf-tools > button { background: linear-gradient(135deg, #2196F3, #42A5F5); color: white; border: none; }
    .btn-pdf-tools > button:hover { background: linear-gradient(135deg, #1976D2, #2196F3); }
    .btn-text > button { background: linear-gradient(135deg, #FF9800, #FFB74D); color: white; border: none; }
    .btn-text > button:hover { background: linear-gradient(135deg, #F57C00, #FF9800); }
    .btn-media > button { background: linear-gradient(135deg, #9C27B0, #BA68C8); color: white; border: none; }
    .btn-media > button:hover { background: linear-gradient(135deg, #7B1FA2, #9C27B0); }
    .btn-transcribe > button { background: linear-gradient(135deg, #009688, #4DB6AC); color: white; border: none; }
    .btn-transcribe > button:hover { background: linear-gradient(135deg, #00796B, #009688); }
    .btn-rdpm > button { background: linear-gradient(135deg, #17a2b8, #5bc0de); color: white; border: none; } /* Exemplo: Azul Ciano */
    .btn-rdpm > button:hover { background: linear-gradient(135deg, #138496, #17a2b8); }
</style>
""", unsafe_allow_html=True)

# Cabeçalho Principal
st.markdown('<h1 class="main-header">🛠️ Ferramentas da Seção de Justiça e Disciplina (P/6)</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-description">Bem-vindo ao portal de ferramentas digitais para otimizar processos administrativos.</p>', unsafe_allow_html=True)

# Layout 2x3 (ou ajuste conforme preferir)
row1_col1, row1_col2 = st.columns(2, gap="medium")
row2_col1, row2_col2 = st.columns(2, gap="medium")
row3_col1, row3_col2 = st.columns(2, gap="medium") # Nova linha para RDPM

with row1_col1:
    st.markdown("""
    <div class="tool-card" id="card-pdf">
        <div> <span class="tool-icon">📄</span> <h2 class="tool-title">Ferramentas PDF</h2> <p>Comprima, OCR, junte, converta PDFs.</p> <ul> <li>Juntar, comprimir, OCR</li> <li>Doc/Planilha/Imagem → PDF</li> <li>PDF → Docx/Imagem</li> </ul> </div>
        <div class="btn-pdf-tools"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    # Usa type="primary" para botões de ação principais
    if st.button("ABRIR FERRAMENTAS PDF", key="pdf_tools_button", use_container_width=True, type="primary"):
         st.switch_page("pages/1_Ferramentas_PDF.py")

with row1_col2:
    st.markdown("""
    <div class="tool-card" id="card-text">
        <div> <span class="tool-icon">📝</span> <h2 class="tool-title">Corretor de Texto</h2> <p>Revise e corrija textos usando IA.</p> <ul> <li>Correção gramatical</li> <li>Ortografia e pontuação</li> <li>Português Brasileiro</li> </ul> </div>
        <div class="btn-text"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR CORRETOR", key="text_button", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Corretor_de_Texto.py")

with row2_col1:
    st.markdown("""
    <div class="tool-card" id="card-media">
        <div> <span class="tool-icon">🎵</span> <h2 class="tool-title">Conversor para MP3</h2> <p>Converta arquivos de vídeo para áudio MP3.</p> <ul> <li>Suporta MP4, AVI, MOV...</li> <li>Extração rápida de áudio</li> <li>Saída em MP3 (192k)</li> </ul> </div>
        <div class="btn-media"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR CONVERSOR MP3", key="media_button", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Video_Audio_Converter.py")

with row2_col2:
    st.markdown("""
    <div class="tool-card" id="card-transcribe">
        <div> <span class="tool-icon">🎤</span> <h2 class="tool-title">Transcritor de Áudio</h2> <p>Converta arquivos de áudio em texto.</p> <ul> <li>Suporta MP3, WAV, M4A...</li> <li>Ideal para reuniões</li> </ul> </div>
        <div class="btn-transcribe"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR TRANSCRITOR", key="transcribe_button", use_container_width=True, type="primary"):
        st.switch_page("pages/4_Audio_Transcripter.py")

# --- CARD PARA RDPM ---
with row3_col1: # Colocado na primeira coluna da terceira linha
    st.markdown("""
    <div class="tool-card" id="card-rdpm">
        <div>
            <span class="tool-icon">⚖️</span>
            <h2 class="tool-title">Consulta RDPM</h2>
            <p>Tire dúvidas sobre o Regulamento Disciplinar.</p>
            <ul>
                <li>Busca no texto oficial</li>
                <li>Respostas baseadas no RDPM</li>
                <li>Assistente IA especializado</li>
            </ul>
        </div>
        <div class="btn-rdpm"></div> <!-- Placeholder -->
    </div>
    """, unsafe_allow_html=True)
    if st.button("CONSULTAR RDPM", key="rdpm_button", use_container_width=True, type="primary"):
        # Verifica se a página existe antes de tentar navegar
        if os.path.exists("pages/5_Consulta_RDPM.py"):
            st.switch_page("pages/5_Consulta_RDPM.py")
        else:
            st.error("Página de Consulta RDPM ainda não implementada.")

# A coluna row3_col2 fica vazia.

# --- Scripts JS para mover os botões (Atualizado) ---
st.markdown("""
    <script>
        function moveButton(cardId, buttonKey, targetDivClass) {
            const card = document.getElementById(cardId);
            // Seletor atualizado para ser mais robusto
            const buttonElement = document.querySelector(`div[data-testid="stButton"][key="${buttonKey}"] > button`);
            if (card && buttonElement) {
                const targetDiv = card.querySelector(`.${targetDivClass}`);
                const buttonContainer = buttonElement.parentElement; // A div.stButton
                // Verifica se o botão já não está no lugar certo para evitar loops infinitos
                if (targetDiv && buttonContainer && targetDiv !== buttonContainer.parentElement) {
                     // Limpa placeholder antes de mover
                    while (targetDiv.firstChild) { targetDiv.removeChild(targetDiv.firstChild); }
                    targetDiv.appendChild(buttonContainer);
                }
            }
        }

        function setupButtonMoves() {
            let attempts = 0;
            const maxAttempts = 15;
            const intervalId = setInterval(() => {
                moveButton('card-pdf', 'pdf_tools_button', 'btn-pdf-tools');
                moveButton('card-text', 'text_button', 'btn-text');
                moveButton('card-media', 'media_button', 'btn-media');
                moveButton('card-transcribe', 'transcribe_button', 'btn-transcribe');
                moveButton('card-rdpm', 'rdpm_button', 'btn-rdpm'); // <<< Adicionado RDPM

                attempts++;
                if (attempts >= maxAttempts) {
                    clearInterval(intervalId);
                }
            }, 300);
        }

        // Executa após o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupButtonMoves);
        } else {
            setupButtonMoves(); // DOM já está pronto
        }
    </script>
    """, unsafe_allow_html=True)


# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
