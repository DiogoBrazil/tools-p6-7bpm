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

        # Inicializa o cliente somente se as credenciais estiverem disponíveis
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
            logging.warning("API Key não encontrada. Configure a variável de ambiente OPENAI_API_KEY.")

    def is_configured(self):
        """Verifica se a API está configurada corretamente."""
        return self.client is not None

    def correct_text(self, text):
        """
        Corrige o texto usando um modelo de linguagem.

        :param text: Texto a ser corrigido
        :return: Texto corrigido ou None em caso de erro
        """
        if not self.is_configured():
            logging.error("API não configurada. Configure a variável de ambiente OPENAI_API_KEY.")
            return None

        if not text or text.strip() == "":
            return ""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                response_format={"type": "text"},
                messages=[
                    {"role": "system",
                     "content": "Você é um professor de português com mais de 20 anos de experiência."},
                    {"role": "user", "content": f'Rescreva apenas o texto a seguir aplicando as normas padrões da língua portuguesa. Retorne apenas o texto corrigido sem comentarios sobre ele ou explicações adcionais: {text}'}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Erro ao corrigir texto: {e}")
            return None
