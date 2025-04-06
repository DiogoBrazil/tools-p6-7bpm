# tools-p-7bpm/Home.py

import streamlit as st
import time # Para delay no JS (pode remover se não usar o JS)
import logging # Para logs (opcional)
import os

# --- Configuração da Página (PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(
    page_title="Ferramentas - 7ºBPM/P-6",
    page_icon="🛠️",
    layout="wide", # Layout largo para acomodar cards
    initial_sidebar_state="collapsed"
)

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
    /* Target primário dentro do card - Seletor mais específico para garantir aplicação */
    div.tool-card div[data-testid="stButton"][type="primary"] > button {
        width: 100%; height: 45px; font-size: 0.95rem; font-weight: bold; transition: all 0.3s ease; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.07); margin-top: auto; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer;
    }
    div.tool-card div[data-testid="stButton"][type="primary"] > button:hover {
        transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* Cores específicas dos botões dos cards (aplicadas via classe no container do botão pelo JS) */
    .btn-pdf-tools > button { background: linear-gradient(135deg, #2196F3, #42A5F5); color: white !important; border: none; }
    .btn-pdf-tools > button:hover { background: linear-gradient(135deg, #1976D2, #2196F3); }
    .btn-text > button { background: linear-gradient(135deg, #FF9800, #FFB74D); color: white !important; border: none; }
    .btn-text > button:hover { background: linear-gradient(135deg, #F57C00, #FF9800); }
    .btn-media > button { background: linear-gradient(135deg, #9C27B0, #BA68C8); color: white !important; border: none; }
    .btn-media > button:hover { background: linear-gradient(135deg, #7B1FA2, #9C27B0); }
    .btn-transcribe > button { background: linear-gradient(135deg, #009688, #4DB6AC); color: white !important; border: none; }
    .btn-transcribe > button:hover { background: linear-gradient(135deg, #00796B, #009688); }
    .btn-rdpm > button { background: linear-gradient(135deg, #17a2b8, #5bc0de); color: white !important; border: none; }
    .btn-rdpm > button:hover { background: linear-gradient(135deg, #138496, #17a2b8); }
    .btn-prescricao > button { background: linear-gradient(135deg, #66bb6a, #81c784); color: white !important; border: none; } /* Estilo novo */
    .btn-prescricao > button:hover { background: linear-gradient(135deg, #4caf50, #66bb6a); }

</style>
""", unsafe_allow_html=True)

# Cabeçalho Principal
st.markdown('<h1 class="main-header">🛠️ Ferramentas da Seção de Justiça e Disciplina (P/6)</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-description">Bem-vindo ao portal de ferramentas digitais para otimizar processos administrativos.</p>', unsafe_allow_html=True)

# Layout 2x3
row1_col1, row1_col2 = st.columns(2, gap="medium")
row2_col1, row2_col2 = st.columns(2, gap="medium")
row3_col1, row3_col2 = st.columns(2, gap="medium") # Terceira linha para RDPM e Prescrição

# --- Card Ferramentas PDF ---
with row1_col1:
    st.markdown("""
    <div class="tool-card" id="card-pdf">
        <div> <span class="tool-icon">📄</span> <h2 class="tool-title">Ferramentas PDF</h2> <p>Comprima, OCR, junte, converta PDFs.</p> <ul> <li>Juntar, comprimir, OCR</li> <li>Doc/Planilha/Imagem → PDF</li> <li>PDF → Docx/Imagem</li> </ul> </div>
        <div class="btn-pdf-tools"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR FERRAMENTAS PDF", key="pdf_tools_button", use_container_width=True, type="primary"):
         st.switch_page("pages/1_Ferramentas_PDF.py")

# --- Card Corretor de Texto ---
with row1_col2:
    st.markdown("""
    <div class="tool-card" id="card-text">
        <div> <span class="tool-icon">📝</span> <h2 class="tool-title">Corretor de Texto</h2> <p>Revise e corrija textos usando IA.</p> <ul> <li>Correção gramatical</li> <li>Ortografia e pontuação</li> <li>Português Brasileiro</li> </ul> </div>
        <div class="btn-text"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR CORRETOR", key="text_button", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Corretor_de_Texto.py")

# --- Card Conversor para MP3 ---
with row2_col1:
    st.markdown("""
    <div class="tool-card" id="card-media">
        <div> <span class="tool-icon">🎵</span> <h2 class="tool-title">Conversor para MP3</h2> <p>Converta arquivos de vídeo para áudio MP3.</p> <ul> <li>Suporta MP4, AVI, MOV...</li> <li>Extração rápida de áudio</li> <li>Saída em MP3 (192k)</li> </ul> </div>
        <div class="btn-media"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR CONVERSOR MP3", key="media_button", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Video_Audio_Converter.py")

# --- Card Transcritor de Áudio ---
with row2_col2:
    st.markdown("""
    <div class="tool-card" id="card-transcribe">
        <div> <span class="tool-icon">🎤</span> <h2 class="tool-title">Transcritor de Áudio</h2> <p>Converta arquivos de áudio em texto.</p> <ul> <li>Suporta MP3, WAV, M4A...</li> <li>Ideal para reuniões</li> </ul> </div>
        <div class="btn-transcribe"></div> <!-- Placeholder -->
    </div>""", unsafe_allow_html=True)
    if st.button("ABRIR TRANSCRITOR", key="transcribe_button", use_container_width=True, type="primary"):
        st.switch_page("pages/4_Audio_Transcripter.py")

# --- Card Consulta RDPM ---
with row3_col1:
    st.markdown("""
    <div class="tool-card" id="card-rdpm">
        <div>
            <span class="tool-icon">⚖️</span>
            <h2 class="tool-title">Consulta RDPM</h2>
            <p>Tire dúvidas sobre o RDPM.</p> <!-- Descrição Atualizada -->
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
        if os.path.exists("pages/5_Consulta_RDPM.py"):
            st.switch_page("pages/5_Consulta_RDPM.py")
        else:
            st.error("Página de Consulta RDPM ainda não implementada.")


# --- Card Calculadora de Prescrição ---
with row3_col2: # Usando a segunda coluna da terceira linha
    st.markdown("""
    <div class="tool-card" id="card-prescricao">
        <div>
            <span class="tool-icon">⏳</span>
            <h2 class="tool-title">Calculadora de Prescrição</h2>
            <p>Calcule prazos prescricionais disciplinares.</p>
            <ul>
                <li>Considera natureza da infração</li>
                <li>Trata interrupções</li>
                <li>Adiciona períodos de suspensão</li>
            </ul>
        </div>
        <div class="btn-prescricao"></div> <!-- Placeholder para o botão -->
    </div>
    """, unsafe_allow_html=True)
    # Botão para a nova página
    if st.button("ABRIR CALCULADORA", key="prescricao_button", use_container_width=True, type="primary"):
        if os.path.exists("pages/6_Calculadora_Prescricao.py"):
            st.switch_page("pages/6_Calculadora_Prescricao.py")
        else:
            st.error("Página da Calculadora de Prescrição não encontrada.")


# --- Scripts JS para mover os botões (Atualizado com Prescrição) ---
st.markdown("""
    <script>
        function moveButton(cardId, buttonKey, targetDivClass) {
            // Encontra o card pelo ID
            const card = document.getElementById(cardId);
            // Encontra o container do botão Streamlit pela key
            const buttonContainer = card ? card.closest('.stApp').querySelector(`div[data-testid="stButton"][key="${buttonKey}"]`) : null;

            if (card && buttonContainer) {
                // Encontra o placeholder dentro do card
                const targetDiv = card.querySelector(`.${targetDivClass}`);
                // Verifica se o botão já não está no lugar certo e se o placeholder existe
                if (targetDiv && targetDiv !== buttonContainer.parentElement) {
                    // Limpa placeholder antes de mover (se necessário)
                    while (targetDiv.firstChild) { targetDiv.removeChild(targetDiv.firstChild); }
                    // Move o container do botão Streamlit para o placeholder
                    targetDiv.appendChild(buttonContainer);
                    // Adiciona a classe de cor ao container do botão (para o CSS funcionar)
                     buttonContainer.classList.add(targetDivClass);
                }
            }
        }

        function setupButtonMoves() {
            let attempts = 0;
            const maxAttempts = 20; // Aumentar tentativas se necessário
            const intervalId = setInterval(() => {
                let allButtonsMoved = true; // Flag para verificar se todos foram movidos

                // Tenta mover cada botão
                allButtonsMoved &= !!moveButton('card-pdf', 'pdf_tools_button', 'btn-pdf-tools');
                allButtonsMoved &= !!moveButton('card-text', 'text_button', 'btn-text');
                allButtonsMoved &= !!moveButton('card-media', 'media_button', 'btn-media');
                allButtonsMoved &= !!moveButton('card-transcribe', 'transcribe_button', 'btn-transcribe');
                allButtonsMoved &= !!moveButton('card-rdpm', 'rdpm_button', 'btn-rdpm');
                allButtonsMoved &= !!moveButton('card-prescricao', 'prescricao_button', 'btn-prescricao'); // <<< Adicionado prescricao

                attempts++;
                // Parar se todos os botões foram movidos ou se atingir maxAttempts
                if (allButtonsMoved || attempts >= maxAttempts) {
                    clearInterval(intervalId);
                    if (attempts >= maxAttempts && !allButtonsMoved) {
                        console.warn("Alguns botões podem não ter sido movidos para os cards após", maxAttempts, "tentativas.");
                    }
                }
            }, 250); // Intervalo ligeiramente menor
        }

        // Garante que o script execute após o DOM ou imediatamente se já estiver pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupButtonMoves);
        } else {
            setupButtonMoves();
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
