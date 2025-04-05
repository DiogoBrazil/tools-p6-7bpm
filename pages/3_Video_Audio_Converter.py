# tools-p-7bpm/pages/3_Video_Audio_Converter.py

import streamlit as st
from modules import media_converter # Importa o novo módulo
import os
import tempfile
import re # Para validar URL do youtube
import time

# --- Constantes ---
# Limite para vídeo/áudio pode ser diferente, ajuste conforme necessário
MAX_MEDIA_SIZE_BYTES = 500 * 1024 * 1024 # 500 MB para vídeos?
MAX_MEDIA_SIZE_MB = MAX_MEDIA_SIZE_BYTES / (1024 * 1024)

# Regex simples para validar URL do YouTube (pode precisar de ajustes)
YOUTUBE_REGEX = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"

# --- Função de Validação ---
def validate_media_file_size(uploaded_file):
    if not uploaded_file: return False
    file_size = uploaded_file.size
    file_size_mb = file_size / (1024 * 1024)
    if file_size > MAX_MEDIA_SIZE_BYTES:
        st.error(f"Arquivo muito grande ({file_size_mb:.1f} MB). O limite máximo é de {MAX_MEDIA_SIZE_MB:.0f} MB.")
        return False
    return True

def validate_youtube_url(url):
    return re.match(YOUTUBE_REGEX, url) is not None

# --- Configuração da Página ---
st.set_page_config(
    page_title="Conversor Vídeo/Áudio - 7ºBPM/P-6",
    page_icon="🎵",
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
    /* Botão de Ação (ex: Roxo) */
    .stButton > button {
        background-color: #9C27B0; color: white; padding: 12px 20px; border: none;
        border-radius: 4px; font-size: 16px; transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #7B1FA2; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transform: translateY(-2px);
    }
    /* Botão Download (Verde) */
    div.stDownloadButton > button {
        background-color: #4CAF50; color: white; padding: 12px 20px; border: none;
        border-radius: 4px; font-size: 16px; transition: all 0.3s;
    }
    div.stDownloadButton > button:hover {
        background-color: #45a049; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- Navegação e Cabeçalho ---
if st.button("← Voltar à página inicial", key="back_button_media_conv"):
    st.switch_page("Home.py")

st.markdown("""
<div class="header-container">
    <div class="header-icon">🎵</div>
    <div>
        <h1>Conversor para MP3</h1>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("Converta arquivos de vídeo ou links do YouTube para formato MP3.")

# --- Seleção de Input ---
input_type = st.radio(
    "Selecione a origem:",
    ('Carregar Arquivo de Vídeo', 'Link do YouTube'),
    key="input_type_media", horizontal=True
)

# --- Placeholders ---
input_placeholder = st.empty()
button_placeholder = st.empty()
result_placeholder = st.empty()

# --- Variáveis de Controle ---
uploaded_file = None
youtube_url = None
output_mp3_data = None
output_filename = "audio.mp3"
processing_triggered = False

# --- Lógica da UI ---
ffmpeg_ok = media_converter._find_ffmpeg() is not None
if not ffmpeg_ok:
    st.error("⚠️ FFmpeg não encontrado no servidor. As conversões não funcionarão.")

if input_type == 'Carregar Arquivo de Vídeo':
    with input_placeholder.container():
        uploaded_file = st.file_uploader(
            f"Carregue um arquivo de vídeo (MP4, AVI, MOV, etc. - Máx: {MAX_MEDIA_SIZE_MB:.0f} MB)",
            type=["mp4", "avi", "mov", "mkv", "webm", "flv"], # Adicione mais tipos se necessário
            key="video_upload"
        )
    if uploaded_file and ffmpeg_ok:
        if validate_media_file_size(uploaded_file):
            processing_triggered = button_placeholder.button("Converter Vídeo para MP3", key="convert_video_btn", use_container_width=True)

elif input_type == 'Link do YouTube':
    with input_placeholder.container():
        youtube_url = st.text_input("Cole o link do vídeo do YouTube:", key="youtube_url_input")
    if youtube_url and ffmpeg_ok:
        if validate_youtube_url(youtube_url):
            processing_triggered = button_placeholder.button("Baixar e Converter Áudio do YouTube", key="convert_youtube_btn", use_container_width=True)
        elif youtube_url: # Se algo foi digitado mas não é válido
             input_placeholder.warning("URL do YouTube inválida. Use o formato padrão (ex: https://www.youtube.com/watch?v=...).")

# --- Processamento ---
if processing_triggered and ffmpeg_ok:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_mp3_path = os.path.join(temp_dir, f"output_{int(time.time())}.mp3")
        success = False
        message = "Falha desconhecida."

        if uploaded_file:
            input_video_path = os.path.join(temp_dir, uploaded_file.name)
            with open(input_video_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            with result_placeholder, st.spinner("Convertendo vídeo para MP3..."):
                success, message = media_converter.convert_video_to_mp3(input_video_path, output_mp3_path)
                output_filename = f"{os.path.splitext(uploaded_file.name)[0]}.mp3"

        elif youtube_url:
            with result_placeholder, st.spinner("Baixando e convertendo áudio do YouTube..."):
                 success, message = media_converter.download_youtube_audio(youtube_url, output_mp3_path)
                 # Tenta gerar um nome mais descritivo (pode falhar se o título não for obtido)
                 try:
                     video_id = re.search(YOUTUBE_REGEX, youtube_url).group(1)
                     output_filename = f"youtube_{video_id}.mp3"
                 except:
                     output_filename = f"youtube_audio_{int(time.time())}.mp3"


        # --- Resultado e Download ---
        if success and os.path.exists(output_mp3_path):
            result_placeholder.success(f"✅ {message}")
            with open(output_mp3_path, "rb") as f:
                output_mp3_data = f.read()
        else:
            result_placeholder.error(f"❌ Falha: {message}")

if output_mp3_data:
    # Limpa placeholder de input/botão e mostra download
    input_placeholder.empty()
    button_placeholder.empty()
    st.download_button(
        label=f"🎵 Baixar {output_filename}",
        data=output_mp3_data,
        file_name=output_filename,
        mime="audio/mpeg",
        key="download_mp3_button",
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
