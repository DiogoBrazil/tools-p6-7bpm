# tools-p-7bpm/Home.py

import streamlit as st

st.set_page_config(
    page_title="Ferramentas - 7ºBPM/P-6",
    page_icon="🛠️",
    layout="wide", # Voltar para 'wide' para melhor acomodar os cards
    initial_sidebar_state="collapsed"
)

# Estilos CSS (Baseado no original, mas com valores reduzidos)
st.markdown("""
<style>
    /* === GERAL === */
    .css-1544g2n { display: none !important; } /* Esconde sidebar */
    /* Container principal com layout wide */
    .block-container {
        max-width: 100%; /* Usa largura total */
        padding: 1.5rem 1.5rem; /* Padding original */
    }
    .main-header {
        font-size: 2.1rem; /* Levemente reduzido */
        margin-bottom: 0.6rem; /* Reduzido */
        text-align: center;
        color: #333;
        font-weight: 600;
    }
    .main-description {
        font-size: 1.0rem;
        margin-bottom: 2rem;
        text-align: center;
        color: #555;
        line-height: 1.6;
    }
    .footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e0e0e6;
        text-align: center;
        font-size: 0.85rem;
        color: #777;
    }

    /* === CARD (REDIMENSIONADO) === */
    .tool-card {
        background-color: #ffffff;
        border-radius: 8px; /* Levemente menor */
        padding: 1.2rem; /* Reduzido */
        margin-bottom: 1.2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        border: 1px solid #e9e9e9;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05); /* Sombra sutil */
        /* min-height: 340px; -> REMOVIDO para deixar o conteúdo definir a altura */
        /* Adicionar uma altura fixa ou max-height se quiser consistência, ex: height: 280px; */
        height: 290px; /* <<< ALTURA FIXA - Ajuste conforme necessário */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* Mantém botão no fundo */
    }
    .tool-card:hover {
        transform: translateY(-4px); /* Efeito hover sutil */
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }

    /* === CONTEÚDO DO CARD (REDIMENSIONADO) === */
    .tool-icon {
        font-size: 2.4rem; /* Reduzido */
        margin-bottom: 0.4rem; /* Reduzido */
        display: block;
    }
    .tool-title {
        font-size: 1.2rem; /* Reduzido */
        margin-bottom: 0.4rem; /* Reduzido */
        color: #2c3e50;
        font-weight: 600; /* Adicionado peso */
    }
    .tool-card p { /* Descrição */
        margin-bottom: 0.5rem; /* Reduzido */
        color: #666;
        line-height: 1.4; /* Reduzido */
        font-size: 0.85rem; /* Reduzido */
    }
    .tool-card ul { /* Lista */
        padding-left: 1rem; /* Reduzido */
        margin: 0.2rem 0 0.6rem 0; /* Margens ajustadas */
        text-align: left;
        color: #555;
        font-size: 0.8rem; /* Reduzido */
    }
    .tool-card li {
        margin-bottom: 0.2rem; /* Reduzido */
    }

    /* === BOTÃO GRANDE NO CARD (REDIMENSIONADO) === */
    .stButton > button {
        width: 100%;
        height: 45px; /* Altura reduzida */
        font-size: 0.95rem; /* Fonte reduzida */
        font-weight: bold;
        transition: all 0.3s ease;
        border-radius: 6px; /* Menor */
        box-shadow: 0 2px 5px rgba(0,0,0,0.07); /* Sombra sutil */
        margin-top: auto; /* Mantém no fundo */
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* Sombra hover */
    }

    /* Cores específicas (mantidas) */
    .btn-pdf-tools > button { background: linear-gradient(135deg, #2196F3, #42A5F5); color: white; }
    .btn-pdf-tools > button:hover { background: linear-gradient(135deg, #1976D2, #2196F3); }
    .btn-text > button { background: linear-gradient(135deg, #FF9800, #FFB74D); color: white; }
    .btn-text > button:hover { background: linear-gradient(135deg, #F57C00, #FF9800); }
    .btn-media > button { background: linear-gradient(135deg, #9C27B0, #BA68C8); color: white; }
    .btn-media > button:hover { background: linear-gradient(135deg, #7B1FA2, #9C27B0); }
    .btn-transcribe > button { background: linear-gradient(135deg, #009688, #4DB6AC); color: white; }
    .btn-transcribe > button:hover { background: linear-gradient(135deg, #00796B, #009688); }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<h1 class="main-header">🛠️ Ferramentas da Seção de Justiça e Disciplina (P/6)</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-description">Bem-vindo ao portal de ferramentas digitais para otimizar processos administrativos.</p>', unsafe_allow_html=True)

# --- Layout 2x2 com Cards ---
row1_col1, row1_col2 = st.columns(2, gap="medium")
row2_col1, row2_col2 = st.columns(2, gap="medium")

# --- Estrutura HTML dos Cards Restaurada ---
with row1_col1:
    st.markdown("""
    <div class="tool-card" id="card-pdf">
        <div> <!-- Conteúdo do Card -->
            <span class="tool-icon">📄</span>
            <h2 class="tool-title">Ferramentas PDF</h2>
            <p>Comprima, OCR, junte, converta PDFs.</p> <!-- Descrição mais curta -->
            <ul>
                <li>Juntar, comprimir, OCR</li>
                <li>Doc/Planilha/Imagem → PDF</li>
                <li>PDF → Docx/Imagem</li>
            </ul>
        </div>
        <div class="btn-pdf-tools"></div> <!-- Placeholder para o botão -->
    </div>
    """, unsafe_allow_html=True)
    # Botão criado fora, movido pelo JS
    if st.button("ABRIR FERRAMENTAS PDF", key="pdf_tools_button", use_container_width=True):
         st.switch_page("pages/1_Ferramentas_PDF.py")

with row1_col2:
    st.markdown("""
    <div class="tool-card" id="card-text">
        <div>
            <span class="tool-icon">📝</span>
            <h2 class="tool-title">Corretor de Texto</h2>
            <p>Revise e corrija textos usando IA.</p> <!-- Descrição mais curta -->
            <ul>
                <li>Correção gramatical</li>
                <li>Ortografia e pontuação</li>
                <li>Português Brasileiro</li>
            </ul>
        </div>
        <div class="btn-text"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ABRIR CORRETOR", key="text_button", use_container_width=True):
        st.switch_page("pages/2_Corretor_de_Texto.py")

with row2_col1:
    st.markdown("""
    <div class="tool-card" id="card-media">
        <div>
            <span class="tool-icon">🎵</span>
            <h2 class="tool-title">Conversor para MP3</h2>
            <p>Converta arquivos de vídeo para áudio MP3.</p> <!-- Descrição mais curta -->
            <ul>
                <li>Suporta MP4, AVI, MOV...</li>
                <li>Extração rápida de áudio</li>
                <li>Saída em MP3 (192k)</li>
            </ul>
        </div>
        <div class="btn-media"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ABRIR CONVERSOR MP3", key="media_button", use_container_width=True):
        st.switch_page("pages/3_Video_Audio_Converter.py")

with row2_col2:
    st.markdown("""
    <div class="tool-card" id="card-transcribe">
        <div>
            <span class="tool-icon">🎤</span>
            <h2 class="tool-title">Transcritor de Áudio</h2>
            <p>Converta arquivos de áudio em texto.</p> <!-- Descrição mais curta -->
            <ul>
                <li>Suporta MP3, WAV, M4A...</li>
                <li>Ideal para reuniões</li>
            </ul>
        </div>
        <div class="btn-transcribe"></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ABRIR TRANSCRITOR", key="transcribe_button", use_container_width=True):
        st.switch_page("pages/4_Audio_Transcripter.py")


# --- Scripts JS para mover os botões (Restaurado) ---
st.markdown("""
    <script>
        function moveButton(cardId, buttonKey, targetDivClass) {
            const card = document.getElementById(cardId);
            // Tenta encontrar o botão pelo seletor mais específico do Streamlit
            const buttonElement = document.querySelector(`button[data-testid='stButton'][kind='primary'][key='${buttonKey}']`);

            if (card && buttonElement) {
                const targetDiv = card.querySelector(`.${targetDivClass}`);
                if (targetDiv) {
                    const buttonContainer = buttonElement.closest('div.stButton');
                    if (buttonContainer) {
                        // Limpa o targetDiv antes de adicionar (evita duplicatas em re-renderizações rápidas)
                        while (targetDiv.firstChild) {
                            targetDiv.removeChild(targetDiv.firstChild);
                        }
                        targetDiv.appendChild(buttonContainer);
                    } else { console.warn(`Button container not found for key ${buttonKey}`); }
                } else { console.warn(`Target div .${targetDivClass} not found in card ${cardId}`); }
            } else {
                 // Silencia logs se não encontrar imediatamente, pode ser timing
                 // if (!card) console.warn(`Card with ID ${cardId} not found.`);
                 // if (!buttonElement) console.warn(`Button with key ${buttonKey} not found.`);
             }
        }

        // Função para executar o movimento dos botões repetidamente em intervalos curtos
        // Isso ajuda a lidar com a renderização assíncrona do Streamlit
        function setupButtonMoves() {
            const intervalId = setInterval(() => {
                moveButton('card-pdf', 'pdf_tools_button', 'btn-pdf-tools');
                moveButton('card-text', 'text_button', 'btn-text');
                moveButton('card-media', 'media_button', 'btn-media');
                moveButton('card-transcribe', 'transcribe_button', 'btn-transcribe');

                // Opcional: parar o intervalo após alguns segundos se tudo estiver estável
                // setTimeout(() => clearInterval(intervalId), 5000); // Para após 5s
            }, 250); // Tenta mover a cada 250ms
        }

        // Garante que o DOM esteja pronto antes de tentar mover
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupButtonMoves);
        } else {
            setupButtonMoves(); // DOM já está pronto
        }

    </script>
""", unsafe_allow_html=True)


# Rodapé (mantido)
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
