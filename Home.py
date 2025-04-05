# tools-p-7bpm/Home.py

import streamlit as st

st.set_page_config(
    page_title="Ferramentas - 7ºBPM/P-6",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados (ajustados para 2 colunas principais ou mantendo 3 com a primeira mais destacada)
st.markdown("""
<style>
    /* ... (Estilos anteriores - Esconder sidebar, layout principal, etc) ... */
    .css-1544g2n { display: none !important; }
    .css-1d391kg, .block-container { max-width: 100%; padding: 1rem 2rem; }
    .main-header { font-size: 2.5rem; margin-bottom: 1rem; text-align: center; color: #333; }
    .main-description { font-size: 1.1rem; margin-bottom: 2.5rem; text-align: center; color: #555; }

    .tool-card { /* Estilo geral do card mantido */
        background-color: #ffffff; border-radius: 12px; padding: 1.8rem; margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease; text-align: center;
        border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        min-height: 400px; /* Aumentar altura mínima se necessário */
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .tool-card:hover { transform: translateY(-6px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); }
    .tool-icon { font-size: 3.5rem; margin-bottom: 0.8rem; display: block; }
    .tool-title { font-size: 1.6rem; margin-bottom: 0.8rem; color: #2c3e50; }
    .tool-card p { margin-bottom: 1rem; color: #666; line-height: 1.6; }
    .tool-card ul { padding-left: 1.5rem; margin: 0.5rem 0 1rem 0; text-align: left; color: #555; }
    .tool-card li { margin-bottom: 0.4rem; }

    /* Botões Grandes */
    .stButton > button { /* Estilo geral do botão mantido */
        width: 100%; height: 65px; font-size: 1.2rem; font-weight: bold;
        transition: all 0.3s ease; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-top: auto; display: flex; align-items: center; justify-content: center;
        border: none; cursor: pointer;
    }
    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }

    /* Cores específicas (PDF agora é azul, Texto laranja?) - Ajuste como preferir */
    .btn-pdf-tools > button { background: linear-gradient(135deg, #2196F3, #42A5F5); color: white; } /* Azul */
    .btn-pdf-tools > button:hover { background: linear-gradient(135deg, #1976D2, #2196F3); }

    .btn-text > button { background: linear-gradient(135deg, #FF9800, #FFB74D); color: white; } /* Laranja */
    .btn-text > button:hover { background: linear-gradient(135deg, #F57C00, #FF9800); }

    /* Remover estilo btn-transform se não houver 3ª coluna */

    .footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e6; text-align: center; font-size: 0.9rem; color: #777; }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<h1 class="main-header">🛠️ Ferramentas da Seção de Justiça e Disciplina (P/6)</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-description">Bem-vindo ao portal de ferramentas digitais para otimizar processos administrativos.</p>', unsafe_allow_html=True)

# --- Ferramentas em 2 Colunas ---
col1, col2 = st.columns(2, gap="large") # Ajustado para 2 colunas

with col1:
    # Card Atualizado para Ferramentas PDF
    st.markdown("""
    <div class="tool-card">
        <div>
            <span class="tool-icon">📄</span> <!-- Ícone atualizado -->
            <h2 class="tool-title">Ferramentas PDF</h2> <!-- Título atualizado -->
            <p>Comprima, adicione OCR (pesquisa) e converta arquivos PDF e documentos.</p> <!-- Descrição atualizada -->
            <ul style="text-align: left;">
                <li>Comprimir PDF e torná-los pesquisáveis (OCR)</li>
                <li>Converter documentos e imagens para PDF</li>
                <li>Converter PDF para DOCX / Imagens</li>
            </ul>
        </div>
        <div class="btn-pdf-tools"></div> <!-- Classe CSS atualizada -->
    </div>
    """, unsafe_allow_html=True)

    # Botão aponta para a nova página consolidada
    if st.button("📄 ABRIR FERRAMENTAS PDF", key="pdf_tools_button", use_container_width=True):
         st.switch_page("pages/1_Ferramentas_PDF.py") # Caminho atualizado

    # Script JS para mover o botão (ajustar seletor se necessário)
    st.markdown("""
        <script>
            // A lógica assume que este é o primeiro card/botão na ordem do código
            const pdfToolsCard = document.querySelector('.tool-card:has(.btn-pdf-tools)');
            if (pdfToolsCard) {
                 const pdfToolsButton = pdfToolsCard.nextElementSibling.querySelector('button');
                 if (pdfToolsButton) {
                     pdfToolsCard.querySelector('.btn-pdf-tools').appendChild(pdfToolsButton.parentNode);
                 }
            }
        </script>
        """, unsafe_allow_html=True)


with col2:
    # Card do Corretor de Texto (inalterado)
    st.markdown("""
    <div class="tool-card">
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

    # Script JS para mover o botão (ajustar seletor se necessário)
    st.markdown("""
        <script>
            // A lógica assume que este é o segundo card/botão
            const textCard = document.querySelectorAll('.tool-card')[1]; // Pega o segundo card
            if(textCard && textCard.querySelector('.btn-text')) { // Verifica se o card e o div existem
                 const textButtonElement = textCard.nextElementSibling; // Pega o elemento do botão Streamlit
                 if (textButtonElement) {
                      const textButton = textButtonElement.querySelector('button');
                      if(textButton){
                           textCard.querySelector('.btn-text').appendChild(textButton.parentNode);
                      }
                 }
            }
        </script>
        """, unsafe_allow_html=True)

# Rodapé
st.markdown("---")
# ... (Rodapé existente inalterado) ...
st.markdown("""
<div class="footer">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
