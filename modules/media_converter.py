# tools-p-7bpm/modules/media_converter.py

import os
import tempfile
import subprocess
import logging
import yt_dlp
import whisper # openai-whisper
import shutil

logging.basicConfig(level=logging.INFO)

# Carrega o modelo Whisper uma vez (pode consumir memória)
# Escolha o modelo: "tiny", "base", "small", "medium", "large"
# Modelos menores são mais rápidos, maiores são mais precisos.
# 'base' ou 'small' são bons pontos de partida.
WHISPER_MODEL_NAME = "base"
whisper_model = None
ffmpeg_path = None

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

def _load_whisper_model():
    """Carrega o modelo Whisper se ainda não estiver carregado."""
    global whisper_model
    if whisper_model:
        return whisper_model
    try:
        logging.info(f"Carregando modelo Whisper '{WHISPER_MODEL_NAME}'...")
        whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
        logging.info("Modelo Whisper carregado com sucesso.")
        return whisper_model
    except Exception as e:
        logging.error(f"Erro ao carregar modelo Whisper '{WHISPER_MODEL_NAME}': {e}")
        return None

# Funções independentes em vez de uma classe por enquanto

def convert_video_to_mp3(input_video_path, output_mp3_path):
    """Converte um arquivo de vídeo para MP3 usando ffmpeg."""
    ffmpeg = _find_ffmpeg()
    if not ffmpeg: return False, "FFmpeg não encontrado."

    command = [
        ffmpeg,
        '-i', input_video_path,  # Arquivo de entrada
        '-vn',                   # Desabilita vídeo (apenas áudio)
        '-acodec', 'libmp3lame',  # Codec de áudio MP3
        '-ab', '192k',           # Bitrate do áudio (ajuste se necessário)
        '-ar', '44100',          # Taxa de amostragem
        '-y',                    # Sobrescreve o arquivo de saída se existir
        output_mp3_path
    ]
    logging.info(f"Executando conversão video->mp3: {' '.join(command)}")
    try:
        process = subprocess.run(command, capture_output=True, check=False, text=True, timeout=300) # Timeout 5 min
        if process.returncode != 0:
            error_msg = f"Erro no FFmpeg (código {process.returncode}): {process.stderr}"
            logging.error(error_msg)
            if os.path.exists(output_mp3_path): os.unlink(output_mp3_path)
            return False, error_msg
        if not os.path.exists(output_mp3_path) or os.path.getsize(output_mp3_path) == 0:
             error_msg = "FFmpeg terminou sem erro, mas o arquivo MP3 não foi criado ou está vazio."
             logging.error(error_msg)
             return False, error_msg

        logging.info("Conversão vídeo->MP3 concluída com sucesso.")
        return True, "Conversão concluída com sucesso."
    except subprocess.TimeoutExpired:
        logging.error("Conversão vídeo->MP3 excedeu o tempo limite.")
        if os.path.exists(output_mp3_path): os.unlink(output_mp3_path)
        return False, "Conversão excedeu o tempo limite."
    except Exception as e:
        error_msg = f"Erro inesperado na conversão vídeo->MP3: {str(e)}"
        logging.error(error_msg)
        if os.path.exists(output_mp3_path): os.unlink(output_mp3_path)
        return False, error_msg


def download_youtube_audio(youtube_url, output_path):
    """Baixa o áudio do YouTube e o salva no formato desejado (MP3)."""
    ffmpeg = _find_ffmpeg()
    if not ffmpeg: return False, "FFmpeg não encontrado, necessário para garantir formato MP3."

    # Diretório temporário para o download inicial do yt-dlp
    temp_dir = os.path.dirname(output_path)
    # yt-dlp pode baixar em formatos como webm, m4a, etc. Usamos um nome base temporário.
    temp_download_path_base = os.path.join(temp_dir, "temp_audio_download")

    ydl_opts = {
        'format': 'bestaudio/best', # Tenta baixar a melhor qualidade de áudio
        'outtmpl': f'{temp_download_path_base}.%(ext)s', # Define o template de nome de arquivo temporário
        'noplaylist': True,         # Não baixa playlists inteiras se um link de vídeo for dado
        'quiet': True,              # Menos output no console
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', # Pede para o yt-dlp converter para mp3
            'preferredquality': '192', # Qualidade do MP3
        }],
        'ffmpeg_location': ffmpeg, # Informa ao yt-dlp onde está o ffmpeg
        'keepvideo': False,       # Não manter o arquivo de vídeo original se baixar um
    }

    logging.info(f"Iniciando download do áudio do YouTube: {youtube_url}")
    downloaded_correctly = False
    status_message = "Falha no download/conversão."

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([youtube_url])

        # yt-dlp já deve ter criado o arquivo final como MP3 devido ao postprocessor
        # O nome final esperado será temp_download_path_base + ".mp3"
        expected_mp3_path = f"{temp_download_path_base}.mp3"

        if error_code == 0 and os.path.exists(expected_mp3_path):
            logging.info(f"Download e conversão pelo yt-dlp bem-sucedidos: {expected_mp3_path}")
            # Renomeia/move o arquivo temporário para o nome final desejado
            shutil.move(expected_mp3_path, output_path)
            logging.info(f"Arquivo final salvo em: {output_path}")
            downloaded_correctly = True
            status_message = "Download e conversão concluídos com sucesso."
        elif error_code != 0:
             status_message = f"yt-dlp falhou com código de erro {error_code}."
             logging.error(status_message)
        else: # error_code == 0 mas arquivo não encontrado
             status_message = "yt-dlp terminou sem erro, mas o arquivo MP3 esperado não foi encontrado."
             logging.error(status_message)

    except yt_dlp.utils.DownloadError as e:
        status_message = f"Erro de download do yt-dlp: {e}"
        logging.error(status_message)
    except Exception as e:
        status_message = f"Erro inesperado durante download/conversão do YouTube: {e}"
        logging.error(status_message)
    finally:
         # Limpeza de arquivos temporários que possam ter sobrado (ex: .webm, .part)
         # yt-dlp é bom em limpar, mas garantimos.
         temp_files = [f for f in os.listdir(temp_dir) if f.startswith(os.path.basename(temp_download_path_base))]
         for temp_file in temp_files:
              file_path = os.path.join(temp_dir, temp_file)
              # Não deleta o arquivo de saída final se ele foi movido corretamente
              if file_path != output_path and os.path.exists(file_path):
                   try:
                        os.unlink(file_path)
                        logging.info(f"Arquivo temporário removido: {temp_file}")
                   except OSError as unlink_err:
                        logging.warning(f"Não foi possível remover arquivo temporário {temp_file}: {unlink_err}")

    return downloaded_correctly, status_message

def transcribe_audio_file(input_audio_path):
    """Transcreve um arquivo de áudio usando Whisper."""
    _find_ffmpeg() # Garante que o path ffmpeg foi verificado (whisper precisa dele)
    model = _load_whisper_model()
    if not model:
        return False, "Modelo Whisper não pôde ser carregado.", ""

    logging.info(f"Iniciando transcrição do arquivo: {input_audio_path}")
    try:
        # Definir o idioma pode melhorar a precisão, mas 'None' detecta automaticamente
        result = model.transcribe(input_audio_path, language=None, fp16=False) # fp16=False para maior compatibilidade CPU
        transcribed_text = result["text"]
        logging.info("Transcrição concluída com sucesso.")
        # logging.debug(f"Texto transcrito: {transcribed_text[:200]}...") # Loga parte do texto para debug
        return True, "Transcrição concluída com sucesso.", transcribed_text
    except Exception as e:
        error_msg = f"Erro durante a transcrição: {e}"
        logging.exception(error_msg) # Loga o traceback completo
        return False, error_msg, ""
