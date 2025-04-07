import streamlit as st
from modules.text_corrector import TextCorrector

st.set_page_config(
    page_title="Corretor de Texto - 7ºBPM/P-6",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"  # Mantém a sidebar fechada
)

# CSS
st.write("""
<style>
    /* Esconde a sidebar completamente */
    .css-1544g2n {
        display: none !important;
    }

    /* Ajusta o layout */
    .css-1d391kg, .block-container {
        max-width: 1200px;
        padding-left: 1rem;
        padding-right: 1rem;
        margin: 0 auto;
    }

    /* Estilo para o botão de voltar */
    div.element-container:nth-child(1) button {
        background-color: #f0f2f6 !important;
        color: #333 !important;
        border: none !important;
        font-weight: normal !important;
    }

    div.element-container:nth-child(1) button:hover {
        background-color: #e0e2e6 !important;
        box-shadow: none !important;
    }

    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }

    .header-icon {
        font-size: 2.5em;
        margin-right: 15px;
    }

    div.stDownloadButton > button {
        background-color: #2196F3;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        transition-duration: 0.4s;
    }

    div.stDownloadButton > button:hover {
        background-color: #0b7dda;
        box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
    }

    .stButton > button {
        background-color: #2196F3;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        transition-duration: 0.4s;
    }

    .stButton > button:hover {
        background-color: #0b7dda;
        box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
    }

    .text-area-label {
        font-weight: bold;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

if st.button("← Voltar à página inicial", key="back_button"):
    st.switch_page("Home.py")

st.markdown("""
<div class="header-container">
    <div class="header-icon">📝</div>
    <div>
        <h1>Corretor de Texto</h1>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Este corretor utiliza inteligência artificial para corrigir textos automaticamente,
aplicando as normas padrões da língua portuguesa.
""")

# Inicializar o corretor de texto
corrector = TextCorrector()

# Verificar se o corretor está configurado
if not corrector.is_configured():
    st.error("""
    ⚠️ **API não configurada!**

    Este serviço requer uma chave de API para funcionar.
    Adicione a variável de ambiente `OPENAI_API_KEY` ou crie um arquivo `.env` com esta variável.

    Contate o administrador do sistema para configurar a API.
    """)

# Caixa de texto para entrada do usuário
st.markdown('<p class="text-area-label">📄 Cole o texto a ser corrigido:</p>', unsafe_allow_html=True)
user_input = st.text_area("", height=250)

# Botão para corrigir o texto
if st.button('Corrigir Texto', use_container_width=True):
    if not user_input.strip():
        st.warning("⚠️ Por favor, insira algum texto para corrigir.")
    else:
        with st.spinner('Corrigindo o texto... Aguarde.'):
            corrected_text = corrector.correct_text(user_input)

        if corrected_text:
            st.success("✅ Texto corrigido com sucesso!")

            st.markdown('<p class="text-area-label">📝 Texto corrigido:</p>', unsafe_allow_html=True)
            st.text_area("", value=corrected_text, height=250, key="corrected")

            # Comparação lado a lado (opcional)
            st.subheader("📊 Comparação")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Texto Original:**")
                st.markdown(f"```{user_input[:500]}{'...' if len(user_input) > 500 else ''}```")

            with col2:
                st.markdown("**Texto Corrigido:**")
                st.markdown(f"```{corrected_text[:500]}{'...' if len(corrected_text) > 500 else ''}```")

            # Botão de download
            st.markdown("### 📥 Download")
            st.download_button(
                label="📄 Baixar texto corrigido",
                data=corrected_text,
                file_name="texto_corrigido.txt",
                mime="text/plain"
            )
        else:
            st.error("❌ Não foi possível corrigir o texto. Tente novamente mais tarde.")

# Informações adicionais no rodapé
st.markdown("---")
st.markdown("""
### 💡 Dicas de uso

- Cole textos completos para obter melhores resultados
- O corretor mantém o estilo e conteúdo original, mas corrige erros gramaticais e ortográficos
- Ideal para documentos oficiais, relatórios e comunicações formais
""")

# Rodapé
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e6e6e6; text-align: center; font-size: 0.9rem; color: #666;">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
