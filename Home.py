# tools-p-7bpm/Home.py

import streamlit as st

st.set_page_config(
    page_title="Ferramentas - 7ºBPM/P-6",
    page_icon="🛠️",
    layout="wide", # Mantém layout largo
    initial_sidebar_state="collapsed"
)

# Estilos CSS (Com ajustes para diminuir os cards e incluir estilos para novos botões)
st.markdown("""
<style>
    /* === GERAL === */
    .css-1544g2n { display: none !important; } /* Esconde sidebar */
    .css-1d391kg, .block-container { max-width: 100%; padding: 1rem 1.5rem; } /* Padding lateral ajustado */
    .main-header { font-size: 2.3rem; margin-bottom: 0.8rem; text-align: center; color: #333; }
    .main-description { font-size: 1.0rem; margin-bottom: 2rem; text-align: center; color: #555; }
    .footer { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e6; text-align: center; font-size: 0.85rem; color: #777; }

    /* === CARD === */
    .tool-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        border: 1px solid #e9e9e9;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        min-height: 340px; /* Altura mínima reduzida */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.08);
    }

    /* === CONTEÚDO DO CARD === */
    .tool-icon {
        font-size: 3.0rem;
        margin-bottom: 0.6rem;
        display: block;
    }
    .tool-title {
        font-size: 1.4rem;
        margin-bottom: 0.6rem;
        color: #2c3e50;
    }
    .tool-card p { /* Descrição */
        margin-bottom: 0.8rem;
        color: #666;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    .tool-card ul { /* Lista */
        padding-left: 1.2rem;
        margin: 0.3rem 0 0.8rem 0;
        text-align: left;
        color: #555;
        font-size: 0.9rem;
    }
    .tool-card li {
        margin-bottom: 0.3rem;
    }

    /* === BOTÃO GRANDE NO CARD === */
    .stButton > button {
        width: 100%;
        height: 55px; /* Altura reduzida */
        font-size: 1.05rem; /* Fonte reduzida */
        font-weight: bold;
        transition: all 0.3s ease;
        border-radius: 8px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.08);
        margin-top: auto; /* Mantém no fundo */
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    }

    /* Cores específicas */
    .btn-pdf-tools > button { background: linear-gradient(135deg, #2196F3, #42A5F5); color: white; } /* Azul */
    .btn-pdf-tools > button:hover { background: linear-gradient(135deg, #1976D2, #2196F3); }

    .btn-text > button { background: linear-gradient(135deg, #FF9800, #FFB74D); color: white; } /* Laranja */
    .btn-text > button:hover { background: linear-gradient(135deg, #F57C00, #FF9800); }

    .btn-media > button { background: linear-gradient(135deg, #9C27B0, #BA68C8); color: white; } /* Roxo */
    .btn-media > button:hover { background: linear-gradient(135deg, #7B1FA2, #9C27B0); }

    .btn-transcribe > button { background: linear-gradient(135deg, #009688, #4DB6AC); color: white; } /* Verde-azulado */
    .btn-transcribe > button:hover { background: linear-gradient(135deg, #00796B, #009688); }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<h1 class="main-header">🛠️ Ferramentas da Seção de Justiça e Disciplina (P/6)</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-description">Bem-vindo ao portal de ferramentas digitais para otimizar processos administrativos.</p>', unsafe_allow_html=True)

# --- Layout 2x2 ---
row1_col1, row1_col2 = st.columns(2, gap="medium")
row2_col1, row2_col2 = st.columns(2, gap="medium")

with row1_col1:
    # Card Ferramentas PDF
    st.markdown("""
    <div class="tool-card" id="card-pdf">
        <div>
            <span class="tool-icon">📄</span>
            <h2 class="tool-title">Ferramentas PDF</h2>
            <p>Comprima, adicione OCR, junte, organize e converta arquivos PDF.</p>
            <ul style="text-align: left;">
                <li>Juntar ou comprimir PDF e aplicar OCR</li>
                <li>Converter Doc/Imagem para PDF</li>
                <li>Converter PDF para Docx/Imagem</li>
            </ul>
        </div>
        <div class="btn-pdf-tools"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📄 ABRIR FERRAMENTAS PDF", key="pdf_tools_button", use_container_width=True):
         st.switch_page("pages/1_Ferramentas_PDF.py")

with row1_col2:
    # Card Corretor de Texto
    st.markdown("""
    <div class="tool-card" id="card-text">
        <div>
            <span class="tool-icon">📝</span>
            <h2 class="tool-title">Corretor de Texto</h2>
            <p>Utilize IA para revisar e corrigir textos em português.</p>
            <ul>
                <li>Correção gramatical e ortográfica</li>
                <li>Melhora clareza e formalidade</li>
                <li>Ideal para documentos oficiais</li>
            </ul>
        </div>
        <div class="btn-text"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📝 ABRIR CORRETOR", key="text_button", use_container_width=True):
        st.switch_page("pages/2_Corretor_de_Texto.py")

with row2_col1:
    # Card Conversor Vídeo/Áudio
    st.markdown("""
    <div class="tool-card" id="card-media">
        <div>
            <span class="tool-icon">🎵</span>
            <h2 class="tool-title">Conversor para MP3</h2>
            <p>Converta vídeos (upload ou link YouTube) para áudio MP3.</p>
            <ul>
                <li>Suporta MP4, AVI, MOV, etc.</li>
                <li>Extrai áudio de links do YouTube</li>
                <li>Saída em formato MP3</li>
            </ul>
        </div>
        <div class="btn-media"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎵 ABRIR CONVERSOR MP3", key="media_button", use_container_width=True):
        st.switch_page("pages/3_Video_Audio_Converter.py")

with row2_col2:
    # Card Transcritor de Áudio
    st.markdown("""
    <div class="tool-card" id="card-transcribe">
        <div>
            <span class="tool-icon">🎤</span>
            <h2 class="tool-title">Transcritor de Áudio</h2>
            <p>Converta arquivos de áudio (MP3, WAV, etc.) em texto.</p>
            <ul>
                <li>Usa IA (modelo Whisper)</li>
                <li>Suporta diversos formatos de áudio</li>
                <li>Ideal para reuniões, entrevistas</li>
            </ul>
        </div>
        <div class="btn-transcribe"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎤 ABRIR TRANSCRITOR", key="transcribe_button", use_container_width=True):
        st.switch_page("pages/4_Audio_Transcripter.py")


# --- Scripts JS para mover os botões ---
st.markdown("""
    <script>
        function moveButton(cardId, buttonKey, targetDivClass) {
            const card = document.getElementById(cardId);
            // Encontra o botão baseado na key (Streamlit gera IDs específicos)
            // O seletor pode precisar ser ajustado dependendo da versão do Streamlit
            // Este seletor tenta encontrar o botão pelo atributo 'key' dentro do container data-testid='stButton'
            const buttonElement = document.querySelector(`button[data-testid='stButton'][kind='primary'][key='${buttonKey}']`);

            if (card && buttonElement) {
                const targetDiv = card.querySelector(`.${targetDivClass}`);
                if (targetDiv) {
                    // Move o container pai mais próximo que tem a classe stButton
                    const buttonContainer = buttonElement.closest('div.stButton');
                    if (buttonContainer) {
                        targetDiv.appendChild(buttonContainer);
                     } else { console.warn(`Button container not found for key ${buttonKey}`); }
                 } else { console.warn(`Target div .${targetDivClass} not found in card ${cardId}`); }
            } else {
                 // Adiciona logs para debug se o card ou botão não for encontrado
                 // if (!card) console.warn(`Card with ID ${cardId} not found.`);
                 // if (!buttonElement) console.warn(`Button with key ${buttonKey} not found.`);
             }
        }

        // Chama a função para cada botão após um delay maior para garantir renderização
        // Pode ser necessário aumentar se os elementos demorarem a aparecer no DOM
        setTimeout(() => {
            moveButton('card-pdf', 'pdf_tools_button', 'btn-pdf-tools');
            moveButton('card-text', 'text_button', 'btn-text');
            moveButton('card-media', 'media_button', 'btn-media');
            moveButton('card-transcribe', 'transcribe_button', 'btn-transcribe');
        }, 300); // Delay de 300ms
    </script>
""", unsafe_allow_html=True)


# Rodapé
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
