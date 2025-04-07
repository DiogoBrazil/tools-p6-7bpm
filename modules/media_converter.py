import os
import tempfile
import subprocess
import logging
import whisper
import shutil
import json
import streamlit as st

logging.basicConfig(level=logging.INFO)

WHISPER_MODEL_NAME = "small"

ffmpeg_path = None
ffprobe_path = None

def _find_ffmpeg():
    """Encontra o caminho do ffmpeg."""
    global ffmpeg_path
    if ffmpeg_path: return ffmpeg_path
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        logging.info(f"FFmpeg encontrado em: {ffmpeg_path}")
    else:
        logging.error("FFmpeg não encontrado no PATH. Funções de áudio/vídeo não funcionarão.")
    return ffmpeg_path

def _find_ffprobe():
    """Encontra o caminho do ffprobe."""
    global ffprobe_path
    if ffprobe_path: return ffprobe_path
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        logging.info(f"ffprobe encontrado em: {ffprobe_path}")
    else:
        logging.warning("ffprobe não encontrado no PATH. Verificação de stream de áudio não será possível.")
    return ffprobe_path


@st.cache_resource(show_spinner=False)
def load_whisper_model():
    """Carrega o modelo Whisper especificado"""
    model = None
    try:
        logging.info(f"CACHE MISS ou primeira execução: Carregando modelo Whisper '{WHISPER_MODEL_NAME}'...")
        # Garante que ffmpeg está disponível, pois whisper pode precisar
        if not _find_ffmpeg():
             logging.error("FFmpeg não encontrado, necessário para Whisper.")
             pass
        model = whisper.load_model(WHISPER_MODEL_NAME)
        logging.info(f"Modelo Whisper '{WHISPER_MODEL_NAME}' carregado com sucesso e cacheado.")
        return model
    except Exception as e:
        logging.error(f"Erro CRÍTICO ao carregar modelo Whisper '{WHISPER_MODEL_NAME}': {e}", exc_info=True)
        return None

def _has_audio_stream(input_path):
    """Verifica se o arquivo de mídia contém pelo menos um stream de áudio usando ffprobe."""
    ffprobe = _find_ffprobe()
    if not ffprobe:
        logging.warning("ffprobe não encontrado. Não foi possível verificar streams de áudio antecipadamente.")
        return True, "Verificação de áudio pulada (ffprobe não encontrado)."
    command = [
        ffprobe, '-v', 'quiet', '-print_format', 'json', '-show_streams', '-select_streams', 'a', input_path
    ]
    logging.info(f"Verificando streams de áudio com ffprobe: {' '.join(command)}")
    try:
        process = subprocess.run(command, capture_output=True, check=False, text=True, timeout=60)
        if process.returncode != 0:
            logging.error(f"Erro ao executar ffprobe (código {process.returncode}): {process.stderr}")
            return True, f"Falha ao analisar streams (erro ffprobe: {process.stderr[:100]}...)."
        if not process.stdout.strip():
             logging.warning("ffprobe não retornou dados de stream de áudio (saída vazia).")
             return False, "O arquivo de vídeo selecionado não contém uma trilha de áudio."
        streams_info = json.loads(process.stdout)
        if streams_info and 'streams' in streams_info and streams_info['streams']:
             logging.info("Stream de áudio detectado.")
             return True, "Stream de áudio encontrado."
        else:
             logging.info("Nenhum stream de áudio detectado.")
             return False, "O arquivo de vídeo selecionado não contém uma trilha de áudio."
    except json.JSONDecodeError as json_err:
        logging.error(f"Erro ao decodificar JSON do ffprobe: {json_err}. Saída: {process.stdout}")
        return True, "Falha ao ler informações dos streams (erro JSON)."
    except subprocess.TimeoutExpired:
        logging.error("ffprobe excedeu o tempo limite ao verificar streams de áudio.")
        return True, "Verificação de áudio excedeu o tempo limite."
    except Exception as e:
        logging.error(f"Erro inesperado ao verificar streams de áudio: {str(e)}")
        return True, f"Erro inesperado na verificação de áudio: {str(e)}"

def convert_video_to_mp3(input_video_path, output_mp3_path):
    # ... (código inalterado) ...
    """Converte um arquivo de vídeo para MP3 usando ffmpeg, verificando antes se há áudio."""
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        return False, "FFmpeg não encontrado."
    has_audio, check_msg = _has_audio_stream(input_video_path)
    if not has_audio:
        logging.warning(f"Conversão cancelada: {check_msg} para o arquivo {input_video_path}")
        return False, check_msg
    logging.info(f"Proceguindo com a conversão para MP3 para {input_video_path} ({check_msg})")
    command = [
        ffmpeg, '-i', input_video_path, '-vn', '-acodec', 'libmp3lame', '-ab', '192k', '-ar', '44100', '-y', output_mp3_path
    ]
    logging.info(f"Executando conversão video->mp3: {' '.join(command)}")
    try:
        process = subprocess.run(command, capture_output=True, check=False, text=True, timeout=300)
        if process.returncode != 0:
            error_msg_detail = process.stderr
            error_msg_user = f"Erro no FFmpeg (código {process.returncode})."
            if "Output file #0 does not contain any stream" in error_msg_detail:
                 error_msg_user = "Ocorreu um erro na conversão. O arquivo pode não ter áudio ou estar corrompido."
            else:
                 error_msg_user = "Erro inesperado durante a conversão com FFmpeg."
            logging.error(f"{error_msg_user} Detalhe FFmpeg: {error_msg_detail}")
            if os.path.exists(output_mp3_path):
                try: os.unlink(output_mp3_path)
                except OSError as e: logging.warning(f"Não foi possível remover arquivo de saída parcial {output_mp3_path}: {e}")
            return False, error_msg_user
        if not os.path.exists(output_mp3_path) or os.path.getsize(output_mp3_path) == 0:
             error_msg = "FFmpeg terminou sem erro, mas o arquivo MP3 não foi criado ou está vazio."
             logging.error(error_msg)
             if os.path.exists(output_mp3_path):
                try: os.unlink(output_mp3_path)
                except OSError as e: logging.warning(f"Não foi possível remover arquivo de saída vazio {output_mp3_path}: {e}")
             return False, error_msg
        logging.info("Conversão vídeo->MP3 concluída com sucesso.")
        return True, "Conversão concluída com sucesso."
    except subprocess.TimeoutExpired:
        logging.error("Conversão vídeo->MP3 excedeu o tempo limite.")
        if os.path.exists(output_mp3_path):
             try: os.unlink(output_mp3_path)
             except OSError as e: logging.warning(f"Não foi possível remover arquivo de saída parcial (timeout) {output_mp3_path}: {e}")
        return False, "Conversão excedeu o tempo limite."
    except Exception as e:
        error_msg = f"Erro inesperado na conversão vídeo->MP3: {str(e)}"
        logging.exception(error_msg)
        if os.path.exists(output_mp3_path):
            try: os.unlink(output_mp3_path)
            except OSError as os_err: logging.warning(f"Não foi possível remover arquivo de saída parcial (exceção) {output_mp3_path}: {os_err}")
        return False, "Ocorreu um erro inesperado durante o processamento."


def transcribe_audio_file(input_audio_path, model):
    """Transcreve um arquivo de áudio usando um modelo Whisper pré-carregado."""
    if not model:
        return False, "Modelo Whisper não fornecido ou inválido.", ""
    _find_ffprobe()

    logging.info(f"Iniciando transcrição com Whisper '{WHISPER_MODEL_NAME}': {input_audio_path}")
    try:
        result = model.transcribe(input_audio_path, language='pt', fp16=False)
        transcribed_text = result["text"]
        logging.info("Transcrição Whisper concluída com sucesso.")
        return True, "Transcrição concluída com sucesso.", transcribed_text
    except Exception as e:
        error_msg = f"Erro durante a transcrição com Whisper: {e}"
        logging.exception(error_msg)
        return False, "Ocorreu um erro durante a transcrição.", ""
