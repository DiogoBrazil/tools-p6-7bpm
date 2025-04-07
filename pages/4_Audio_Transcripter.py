import streamlit as st
from modules.media_converter import load_whisper_model, transcribe_audio_file, WHISPER_MODEL_NAME
from modules.text_corrector import TextCorrector
import os
import tempfile
import time
import logging 

MAX_AUDIO_SIZE_BYTES = 200 * 1024 * 1024
MAX_AUDIO_SIZE_MB = MAX_AUDIO_SIZE_BYTES / (1024 * 1024)

def validate_audio_file_size(uploaded_file):
    if not uploaded_file: return False
    file_size = uploaded_file.size
    file_size_mb = file_size / (1024 * 1024)
    if file_size > MAX_AUDIO_SIZE_BYTES:
        st.error(f"Arquivo muito grande ({file_size_mb:.1f} MB). O limite máximo é de {MAX_AUDIO_SIZE_MB:.0f} MB.")
        return False
    return True

# --- Configuração da Página ---
st.set_page_config(
    page_title="Transcritor e Corretor de Áudio - 7ºBPM/P-6",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS Customizado ---
st.write("""
<style>
    /* ... (seu CSS aqui) ... */
    .css-1544g2n { display: none !important; }
    .css-1d391kg, .block-container { max-width: 1000px; padding: 1rem; margin: 0 auto; }
    div.element-container:nth-child(1) { margin-top: 1rem; }
    div.element-container:nth-child(1) > .stButton > button { background-color: #f0f2f6 !important; color: #333 !important; border: 1px solid #d1d1d1 !important; font-weight: normal !important; box-shadow: none !important; }
    div.element-container:nth-child(1) > .stButton > button:hover { background-color: #e0e2e6 !important; color: #111 !important; border-color: #c1c1c1 !important; box-shadow: none !important; }
    .header-container { display: flex; align-items: center; margin-bottom: 20px; }
    .header-icon { font-size: 2.5em; margin-right: 15px; }
    .stButton > button { background-color: #009688; color: white; padding: 12px 20px; border: none; border-radius: 4px; font-size: 16px; transition: all 0.3s; }
    .stButton > button:hover { background-color: #00796B; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transform: translateY(-2px); }
    div.stDownloadButton > button { background-color: #4CAF50; color: white; padding: 12px 20px; border: none; border-radius: 4px; font-size: 16px; transition: all 0.3s; }
    div.stDownloadButton > button:hover { background-color: #45a049; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transform: translateY(-2px); }
    .stTextArea textarea { font-size: 1rem; line-height: 1.6; }
    .transcription-box { margin-bottom: 1.5rem; padding: 1rem; border: 1px solid #eee; border-radius: 5px; background-color: #f8f9fa; }
    .transcription-box h3 { margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem; color: #555;}
</style>
""", unsafe_allow_html=True)

# --- Navegação e Cabeçalho ---
if st.button("← Voltar à página inicial", key="back_button_transcriber"):
    st.switch_page("Home.py")

st.markdown("""
<div class="header-container">
    <div class="header-icon">🎤</div>
    <div>
        <h1>Transcritor e Corretor de Áudio</h1>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("Carregue um áudio (MP3, WAV, etc.) para transcrever e depois refinar a transcrição com IA.")
st.caption("Transcrições e correções de áudios grandes podem demorar alguns minutos. Importante aguardar o processo terminar.")

# --- Inicializações ---
corrector = TextCorrector()
api_corrector_ok = corrector.is_configured()
whisper_model = None # Variável para guardar o modelo carregado

# --- <<< Carregamento do Modelo Whisper com Spinner >>> ---
model_load_status_placeholder = st.empty()
try:
    with model_load_status_placeholder, st.spinner(f"Carregando modelo de transcrição ({WHISPER_MODEL_NAME})... Aguarde. Isso pode levar alguns minutos na primeira vez."):
        whisper_model = load_whisper_model() # Chama a função cacheada
except Exception as load_err:
     # Captura exceções que possam ocorrer fora da função cacheada
     logging.error(f"Erro inesperado durante tentativa de carregar modelo: {load_err}", exc_info=True)
     whisper_model = None # Garante que está None

# --- Verifica se o modelo carregou antes de mostrar o resto ---
if whisper_model is None:
    model_load_status_placeholder.error(f"❌ Falha crítica ao carregar o modelo de transcrição Whisper ({WHISPER_MODEL_NAME}). A funcionalidade de transcrição está indisponível. Verifique os logs do servidor.")
    # Impede a exibição do restante da página se o modelo essencial não carregar
    st.stop()
else:
    # Limpa a mensagem do spinner se carregou com sucesso
    model_load_status_placeholder.empty()
    logging.info("Modelo Whisper pronto para uso.")
    # Aviso sobre API do Corretor
    if not api_corrector_ok:
        st.warning("⚠️ API de correção não configurada (verifique OPENAI_API_KEY no .env). O refinamento pós-transcrição será pulado.")


    # --- Placeholders da UI Principal ---
    upload_placeholder = st.empty()
    button_placeholder = st.empty()
    result_placeholder = st.empty()
    output_placeholder = st.empty()

    # --- Variáveis de Controle ---
    uploaded_file = None
    raw_transcribed_text = None
    corrected_transcribed_text = None
    processing_triggered = False

    # --- Lógica da UI (Uploader e Botão) ---
    with upload_placeholder.container():
        uploaded_file = st.file_uploader(
            f"Carregue um arquivo de áudio (MP3, WAV, M4A, etc. - Máx: {MAX_AUDIO_SIZE_MB:.0f} MB)",
            type=["mp3", "wav", "m4a", "ogg", "flac", "mpga"],
            key="audio_upload"
        )

    if uploaded_file:
        if validate_audio_file_size(uploaded_file):
            # Botão só aparece se o arquivo for válido
            processing_triggered = button_placeholder.button("Transcrever e Corrigir Áudio", key="transcribe_correct_btn", use_container_width=True)

    # --- Processamento em duas etapas ---
    if processing_triggered:
        output_placeholder.empty()
        raw_transcribed_text = None
        corrected_transcribed_text = None

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_audio:
            temp_audio.write(uploaded_file.getvalue())
            input_audio_path = temp_audio.name

        try:
            # Etapa 1: Transcrição com Whisper (passando o modelo carregado)
            with result_placeholder, st.spinner("Etapa 1/2: Transcrevendo áudio..."):
                 # <<< Passa o whisper_model carregado >>>
                transcribe_success, transcribe_message, raw_text = transcribe_audio_file(
                    input_audio_path,
                    model=whisper_model
                )

            if transcribe_success:
                raw_transcribed_text = raw_text
                st.success(f"✅ {transcribe_message}")

                # Etapa 2: Correção com API
                if api_corrector_ok:
                    with result_placeholder, st.spinner("Etapa 2/2: Refinando transcrição com IA..."):
                         corrected_text = corrector.correct_transcription(raw_transcribed_text)

                    if corrected_text is not None:
                        corrected_transcribed_text = corrected_text
                        st.success("✅ Transcrição refinada pela IA com sucesso!")
                    else:
                        st.warning("⚠️ Falha ao refinar transcrição com IA. Exibindo apenas a transcrição original.")
                else:
                     st.info("Refinamento com IA pulado (API não configurada).")

            else:
                result_placeholder.error(f"❌ Falha na transcrição: {transcribe_message}")

        finally:
            if os.path.exists(input_audio_path):
                try: os.unlink(input_audio_path)
                except Exception as e: logging.warning(f"Não foi possível remover o arquivo de áudio temporário {input_audio_path}: {e}")


    # --- Exibir Resultado ---
    if raw_transcribed_text is not None:
        upload_placeholder.empty()
        button_placeholder.empty()
        result_placeholder.empty()

        with output_placeholder.container():
            st.subheader("Resultados:")
            # Caixa 1: Transcrição Original (Whisper)
            with st.container(border=True):
                 st.markdown("**Transcrição Original**")
                 st.text_area("", value=raw_transcribed_text, height=300, key="transcription_raw_output", disabled=True)
                 st.download_button(
                     label="📄 Baixar Transcrição Original (.txt)",
                     data=raw_transcribed_text.encode('utf-8'),
                     file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcricao_whisper.txt",
                     mime="text/plain",
                     key="download_raw_text_button",
                     use_container_width=True
                 )
            st.markdown("---")
            # Caixa 2: Transcrição Refinada (IA)
            if corrected_transcribed_text is not None:
                with st.container(border=True):
                    st.markdown("**Transcrição Refinada**") # Título atualizado
                    st.text_area("", value=corrected_transcribed_text, height=300, key="transcription_corrected_output", disabled=True)
                    st.download_button(
                        label="📄 Baixar Transcrição Refinada (.txt)",
                        data=corrected_transcribed_text.encode('utf-8'),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcricao_corrigida_api.txt",
                        mime="text/plain",
                        key="download_corrected_text_button",
                        use_container_width=True
                    )
            elif api_corrector_ok:
                 st.info("A correção via IA não produziu resultado para este áudio.")


# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e6e6e6; text-align: center; font-size: 0.9rem; color: #666;">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
