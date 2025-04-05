import streamlit as st
from modules import media_converter # Usa o mesmo módulo
import os
import tempfile
import time

# --- Constantes ---
MAX_AUDIO_SIZE_BYTES = 200 * 1024 * 1024 # 200 MB para áudio? Ajuste.
MAX_AUDIO_SIZE_MB = MAX_AUDIO_SIZE_BYTES / (1024 * 1024)

# --- Função de Validação ---
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
    page_title="Transcritor de Áudio - 7ºBPM/P-6",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS Customizado (similar às outras páginas) ---
st.write("""
<style>
    /* ... (CSS básico: sidebar, container, botão voltar) ... */
    .css-1544g2n { display: none !important; }
    .css-1d391kg, .block-container { max-width: 1000px; padding: 1rem; margin: 0 auto; }
    div.element-container:nth-child(1) { margin-top: 1rem; }
    div.element-container:nth-child(1) > .stButton > button { /* Botão Voltar */
        background-color: #f0f2f6 !important; color: #333 !important; border: 1px solid #d1d1d1 !important;
        font-weight: normal !important; box-shadow: none !important;
    }
    div.element-container:nth-child(1) > .stButton > button:hover {
        background-color: #e0e2e6 !important; color: #111 !important; border-color: #c1c1c1 !important;
        box-shadow: none !important;
    }
    /* Cabeçalho */
    .header-container { display: flex; align-items: center; margin-bottom: 20px; }
    .header-icon { font-size: 2.5em; margin-right: 15px; }
    /* Botão de Ação (ex: Verde-azulado) */
    .stButton > button {
        background-color: #009688; color: white; padding: 12px 20px; border: none;
        border-radius: 4px; font-size: 16px; transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #00796B; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transform: translateY(-2px);
    }
     /* Botão Download (Verde padrão) */
    div.stDownloadButton > button {
        background-color: #4CAF50; color: white; padding: 12px 20px; border: none;
        border-radius: 4px; font-size: 16px; transition: all 0.3s;
    }
    div.stDownloadButton > button:hover {
        background-color: #45a049; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transform: translateY(-2px);
    }
    /* Área de texto */
    .stTextArea textarea { font-size: 1rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- Navegação e Cabeçalho ---
if st.button("← Voltar à página inicial", key="back_button_transcriber"):
    st.switch_page("Home.py")

st.markdown("""
<div class="header-container">
    <div class="header-icon">🎤</div>
    <div>
        <h1>Transcritor de Áudio</h1>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("Carregue um arquivo de áudio (MP3, WAV, etc.) para extrair o texto.")
st.caption("Transcrições longas podem demorar.")

# --- Placeholders ---
upload_placeholder = st.empty()
button_placeholder = st.empty()
result_placeholder = st.empty()

# --- Variáveis de Controle ---
uploaded_file = None
transcribed_text = None
output_filename = "transcricao.txt"
processing_triggered = False

# --- Lógica da UI ---
ffmpeg_ok = media_converter._find_ffmpeg() is not None
whisper_model_ok = media_converter._load_whisper_model() is not None # Tenta carregar/verificar modelo

if not ffmpeg_ok:
    st.warning("⚠️ FFmpeg não encontrado. A transcrição pode falhar para alguns formatos.")
if not whisper_model_ok:
     st.error("❌ Modelo Whisper não pôde ser carregado. Transcrição indisponível.")

with upload_placeholder.container():
    uploaded_file = st.file_uploader(
        f"Carregue um arquivo de áudio (MP3, WAV, M4A, etc. - Máx: {MAX_AUDIO_SIZE_MB:.0f} MB)",
        # Whisper suporta vários formatos se ffmpeg estiver instalado
        type=["mp3", "wav", "m4a", "ogg", "flac", "mpga"],
        key="audio_upload"
    )

if uploaded_file and ffmpeg_ok and whisper_model_ok:
    if validate_audio_file_size(uploaded_file):
        processing_triggered = button_placeholder.button("Transcrever Áudio", key="transcribe_btn", use_container_width=True)

# --- Processamento ---
if processing_triggered:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_audio:
        temp_audio.write(uploaded_file.getvalue())
        input_audio_path = temp_audio.name

    try: # Bloco try/finally para garantir limpeza do temp file
        with result_placeholder, st.spinner("Transcrevendo áudio... Isso pode levar vários minutos."):
            success, message, text_result = media_converter.transcribe_audio_file(input_audio_path)

        if success:
            result_placeholder.success("✅ Transcrição concluída!")
            transcribed_text = text_result
            output_filename = f"{os.path.splitext(uploaded_file.name)[0]}_transcricao.txt"
        else:
            result_placeholder.error(f"❌ Falha na transcrição: {message}")

    finally:
        # Limpa o arquivo de áudio temporário
        if os.path.exists(input_audio_path):
            os.unlink(input_audio_path)


# --- Exibir Resultado e Download ---
if transcribed_text is not None:
    upload_placeholder.empty() # Limpa upload e botão
    button_placeholder.empty()
    st.subheader("Texto Transcrito:")
    st.text_area("Transcrição", value=transcribed_text, height=400, key="transcription_output")
    st.download_button(
        label="📄 Baixar Texto (.txt)",
        data=transcribed_text.encode('utf-8'), # Garante codificação UTF-8
        file_name=output_filename,
        mime="text/plain",
        key="download_text_button",
        use_container_width=True
    )

# --- Rodapé ---
st.markdown("---")
# ... (Rodapé padrão) ...
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e6e6e6; text-align: center; font-size: 0.9rem; color: #666;">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
