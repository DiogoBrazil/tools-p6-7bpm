import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

class TextCorrector:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "deepseek-chat") # Permite configurar o modelo via .env

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                logging.info(f"Cliente OpenAI inicializado. Base URL: {self.base_url}, Modelo: {self.model_name}")
            except Exception as e:
                 logging.error(f"Erro ao inicializar cliente OpenAI: {e}")
                 self.client = None
        else:
            self.client = None
            logging.warning("API Key (OPENAI_API_KEY) não encontrada no ambiente/arquivo .env.")

    def is_configured(self):
        """Verifica se a API está configurada corretamente (cliente inicializado)."""
        return self.client is not None

    def correct_text(self, text):
        """
        Corrige texto genérico usando um modelo de linguagem via API.
        Prompt focado em normas padrão da língua portuguesa.
        """
        if not self.is_configured():
            logging.error("API não configurada.")
            return None
        if not text or text.strip() == "": return ""

        try:
            logging.info(f"Enviando texto para correção genérica via API ({self.base_url}, {self.model_name})...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system",
                     "content": "Você é um revisor de texto experiente, focado em corrigir erros gramaticais e ortográficos do Português Brasileiro, mantendo o sentido original."},
                    {"role": "user",
                     "content": f'Corrija o seguinte texto aplicando as normas padrões da língua portuguesa. Retorne APENAS o texto corrigido, sem introduções, explicações ou formatação extra: {text}'}
                ],
                temperature=0.3, # Temperatura baixa para correção mais direta
                max_tokens=int(len(text.split()) * 1.5) + 100 # Estimativa generosa
            )
            corrected_text = response.choices[0].message.content.strip()
            logging.info("Texto corrigido (genérico) recebido da API.")
            return corrected_text
        except Exception as e:
            logging.error(f"Erro ao chamar API de correção genérica ({self.base_url}): {e}")
            return None

    # <<< NOVO MÉTODO para corrigir transcrições >>>
    def correct_transcription(self, text):
        """
        Refina e corrige uma transcrição de áudio (possivelmente de audiência) usando a API.
        Prompt focado em clareza, pontuação, e potenciais termos técnicos/nomes.
        """
        if not self.is_configured():
            logging.error("API não configurada.")
            return None
        if not text or text.strip() == "": return ""

        try:
            logging.info(f"Enviando transcrição para correção/refinamento via API ({self.base_url}, {self.model_name})...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system",
                     "content": """Você é um especialista em transcrever e revisar textos de áudios em português brasileiro, especialmente de contextos formais como audiências ou depoimentos. Sua tarefa é pegar a transcrição bruta fornecida e corrigi-la para torná-la clara, gramaticalmente correta e com pontuação adequada. Preste atenção especial a possíveis nomes próprios, patentes militares (Ex: Capitão, Sargento), termos jurídicos ou técnicos, e tente interpretá-los corretamente mesmo que a transcrição inicial esteja confusa. Mantenha o sentido original do que foi dito."""
                    },
                    {"role": "user",
                     "content": f'Corrija e refine a seguinte transcrição de áudio. Retorne APENAS o texto final corrigido e refinado, sem introduções, comentários ou formatação extra: {text}'}
                ],
                temperature=0.5, # Temperatura um pouco maior para permitir alguma interpretação/refinamento
                max_tokens=int(len(text.split()) * 1.5) + 200 # Estimativa mais generosa para refinamento
            )
            corrected_text = response.choices[0].message.content.strip()
            logging.info("Transcrição corrigida/refinada recebida da API.")
            return corrected_text
        except Exception as e:
            logging.error(f"Erro ao chamar API de correção de transcrição ({self.base_url}): {e}")
            return None
