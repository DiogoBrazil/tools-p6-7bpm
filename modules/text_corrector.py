import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__) # Logger específico para este módulo

class TextCorrector:
    """
    Classe responsável por interagir com uma API de LLM (compatível com OpenAI)
    para tarefas de correção de texto e refinamento de transcrições.
    As credenciais e endpoints da API são lidos de variáveis de ambiente.
    """
    def __init__(self):
        """
        Inicializa o TextCorrector carregando as configurações da API
        e instanciando o cliente OpenAI.
        """
        load_dotenv() # Carrega variáveis do arquivo .env, se existir

        # Lê as configurações do ambiente
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com") # Default DeepSeek
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "deepseek-chat") # Default DeepSeek model

        self.client = None # Inicializa o cliente como None

        # Tenta inicializar o cliente OpenAI se a chave API for fornecida
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                log.info(f"Cliente OpenAI inicializado. Base URL: {self.base_url}, Modelo padrão: {self.model_name}")
            except Exception as e:
                 log.error(f"Erro ao inicializar cliente OpenAI com Base URL '{self.base_url}': {e}", exc_info=True)
        else:
            log.warning("API Key (OPENAI_API_KEY) não encontrada no ambiente ou arquivo .env. Funções de correção via API estarão desabilitadas.")

    def is_configured(self) -> bool:
        """
        Verifica se o cliente da API foi inicializado com sucesso.

        Returns:
            True se o cliente está configurado, False caso contrário.
        """
        return self.client is not None

    def get_llm_client(self) -> OpenAI | None:
        """
        Retorna a instância do cliente OpenAI inicializado.
        Útil para ser usado por outras partes do sistema (como LangChain).

        Returns:
            A instância do cliente OpenAI, ou None se não estiver configurado.
        """
        return self.client

    def correct_text(self, text: str) -> str | None:
        """
        Corrige um texto genérico usando a API configurada.
        Foca em aplicar normas padrão da língua portuguesa.

        Args:
            text: O texto a ser corrigido.

        Returns:
            O texto corrigido como string, ou None se ocorrer um erro ou a API não estiver configurada.
        """
        if not self.is_configured():
            log.error("Tentativa de usar correct_text sem API configurada.")
            return None # Indica falha na configuração
        if not text or not text.strip():
            log.debug("correct_text chamado com texto vazio.")
            return "" # Retorna string vazia para input vazio

        try:
            log.info(f"Enviando texto para correção genérica via API...")
            response = self.client.chat.completions.create(
                model=self.model_name, # Usa o modelo definido na inicialização
                messages=[
                    {"role": "system",
                     "content": "Você é um revisor de texto experiente, focado em corrigir erros gramaticais e ortográficos do Português Brasileiro, mantendo o sentido original."},
                    {"role": "user",
                     "content": f'Corrija o seguinte texto aplicando as normas padrões da língua portuguesa. Retorne APENAS o texto corrigido, sem introduções, explicações ou formatação extra (como ```): {text}'}
                ],
                temperature=0.3, # Temperatura baixa para manter o texto próximo ao original
                max_tokens=int(len(text.split()) * 1.5) + 150 # Estimativa segura para max_tokens
            )

            # Extrai e limpa a resposta
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                corrected_text = response.choices[0].message.content.strip()
                log.info("Texto corrigido (genérico) recebido da API.")
                return corrected_text
            else:
                log.warning(f"Resposta da API de correção genérica inesperada ou vazia: {response}")
                return None # Retorna None se a resposta não for válida

        except Exception as e:
            # Captura e loga erros durante a chamada da API
            log.error(f"Erro ao chamar API de correção genérica ({self.base_url}): {e}", exc_info=True)
            return None # Retorna None para indicar erro na API

    def correct_transcription(self, text: str) -> str | None:
        """
        Refina e corrige uma transcrição de áudio (possivelmente de audiência) usando a API.
        Usa um prompt específico para o contexto de transcrições.

        Args:
            text: A transcrição bruta a ser corrigida/refinada.

        Returns:
            O texto refinado como string, ou None se ocorrer um erro ou a API não estiver configurada.
        """
        if not self.is_configured():
            log.error("Tentativa de usar correct_transcription sem API configurada.")
            return None # Indica falha na configuração
        if not text or not text.strip():
            log.debug("correct_transcription chamado com texto vazio.")
            return "" # Retorna string vazia para input vazio

        try:
            log.info(f"Enviando transcrição para correção/refinamento via API...")
            response = self.client.chat.completions.create(
                model=self.model_name, # Usa o modelo definido na inicialização
                messages=[
                    {"role": "system",
                     "content": """Você é um especialista em transcrever e revisar textos de áudios em português brasileiro, especialmente de contextos formais como audiências ou depoimentos. Sua tarefa é pegar a transcrição bruta fornecida e corrigi-la para torná-la clara, gramaticalmente correta e com pontuação adequada. Preste atenção especial a possíveis nomes próprios, patentes militares (Ex: Capitão, Sargento), termos jurídicos ou técnicos, e tente interpretá-los corretamente mesmo que a transcrição inicial esteja confusa. Mantenha o sentido original do que foi dito."""
                    },
                    {"role": "user",
                     "content": f'Corrija e refine a seguinte transcrição de áudio. Retorne APENAS o texto final corrigido e refinado, sem introduções, comentários ou formatação extra (como ```): {text}'}
                ],
                temperature=0.5, # Temperatura um pouco maior para permitir alguma reestruturação/interpretação
                max_tokens=int(len(text.split()) * 1.5) + 250 # Estimativa mais generosa para refinamento
            )

            # Extrai e limpa a resposta
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                corrected_text = response.choices[0].message.content.strip()
                log.info("Transcrição corrigida/refinada recebida da API.")
                return corrected_text
            else:
                 log.warning(f"Resposta da API de correção de transcrição inesperada ou vazia: {response}")
                 return None # Retorna None se a resposta não for válida

        except Exception as e:
            # Captura e loga erros durante a chamada da API
            log.error(f"Erro ao chamar API de correção de transcrição ({self.base_url}): {e}", exc_info=True)
            return None # Retorna None para indicar erro na API
