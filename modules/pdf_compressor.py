import os
import tempfile
import subprocess
import platform
import shutil
from PyPDF2 import PdfReader, PdfWriter

class PDFCompressor:
    def __init__(self):
        # Determinar o caminho do Ghostscript com base no sistema operacional
        self.gs_cmd = 'gswin64c' if platform.system() == 'Windows' else 'gs'
    
    def is_ocrmypdf_installed(self):
        """Verifica se o OCRmyPDF está instalado e disponível no sistema."""
        try:
            result = subprocess.run(['ocrmypdf', '--version'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True,
                                timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError, Exception):
            return False
    
    def compress_pdf(self, input_file_path, output_file_path, power=3):
        """
        Comprime o arquivo PDF usando Ghostscript.
        
        :param input_file_path: Caminho para o arquivo PDF original
        :param output_file_path: Caminho onde o arquivo PDF comprimido será salvo
        :param power: Nível de compressão (0-4), onde 0 é a menor compressão e 4 a maior
        :return: True se bem-sucedido, False caso contrário
        """
        quality = {
            0: '/default',
            1: '/prepress',
            2: '/printer',
            3: '/ebook',
            4: '/screen'
        }
        
        try:
            subprocess.call([
                self.gs_cmd, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={quality[power]}',
                '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={output_file_path}',
                input_file_path
            ])
            return True
        except Exception as e:
            print(f"Erro ao comprimir o PDF: {str(e)}")
            return False
    
    def apply_ocrmypdf(self, input_path, output_path, language='por'):
        """
        Aplica OCR usando OCRmyPDF.
        
        :param input_path: Caminho para o arquivo PDF
        :param output_path: Caminho para salvar o PDF com OCR
        :param language: Idioma do texto (por = português, eng = inglês)
        :return: True se bem-sucedido, False caso contrário
        """
        try:
            # Cria cópia temporária para processar
            temp_input = input_path + ".tmp.pdf"
            shutil.copy2(input_path, temp_input)
            
            # Configura argumentos do OCRmyPDF
            args = [
                'ocrmypdf',            # Comando
                '--force-ocr',         # Força OCR em todas as páginas
                '--optimize', '1',     # Otimizar pdf (usar 0-3)
                '--output-type', 'pdf', # Saída como PDF
                '--jobs', '2',         # Número de processadores a usar
                '-l', language,        # Idioma
                temp_input,            # Arquivo de entrada
                output_path            # Arquivo de saída
            ]
            
            # Executa OCRmyPDF
            process = subprocess.run(
                args,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Limpa o arquivo temporário
            if os.path.exists(temp_input):
                os.unlink(temp_input)
                
            if process.returncode != 0:
                print(f"Erro no OCRmyPDF: {process.stderr}")
                return False
                
            return True
        except Exception as e:
            print(f"Erro ao executar OCRmyPDF: {str(e)}")
            return False
    
    def process_pdf(self, file_bytes, compression_level=3, apply_ocr=False):
        """
        Processa um arquivo PDF: comprime e aplica OCR se solicitado.
        
        :param file_bytes: Bytes do arquivo PDF
        :param compression_level: Nível de compressão (0-4)
        :param apply_ocr: Se deve aplicar OCR
        :return: Tupla (sucesso, bytes do arquivo processado, tamanho original, tamanho final)
        """
        # Cria arquivo temporário para entrada
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
            temp_input.write(file_bytes)
            input_path = temp_input.name
        
        # Caminhos para os arquivos de saída
        compressed_path = input_path.replace('.pdf', '_comprimido.pdf')
        final_output_path = input_path.replace('.pdf', '_final.pdf')
        
        try:
            original_size = len(file_bytes) / 1024 / 1024  # em MB
            
            # Etapa 1: Compressão
            success = self.compress_pdf(input_path, compressed_path, compression_level)
            
            # Etapa 2: OCR (se solicitado)
            if success and apply_ocr:
                ocr_success = self.apply_ocrmypdf(compressed_path, final_output_path)
                output_path = final_output_path if ocr_success else compressed_path
            else:
                output_path = compressed_path
            
            if success:
                # Le o arquivo processado
                with open(output_path, 'rb') as f:
                    processed_bytes = f.read()
                
                # Tamanho final
                final_size = len(processed_bytes) / 1024 / 1024  # em MB
                
                return (True, processed_bytes, original_size, final_size)
            else:
                return (False, None, original_size, 0)
        
        finally:
            # Limpeza dos arquivos temporários
            for path in [input_path, compressed_path, final_output_path]:
                if os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass