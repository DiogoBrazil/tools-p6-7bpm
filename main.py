import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import subprocess
import platform
import shutil

st.set_page_config(page_title="Compressor de PDF", page_icon="📄")

def get_ghostscript_path():
    """Retorna o caminho para o executável do Ghostscript com base no sistema operacional."""
    if platform.system() == 'Windows':
        # Em Windows, normalmente o ghostscript está instalado em Program Files
        return 'gswin64c'  # Para Windows 64-bit
    else:
        # Em sistemas Unix (Linux/Mac), o ghostscript geralmente está disponível no PATH
        return 'gs'

def compress_pdf(input_file_path, output_file_path, power=3):
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
    
    gs = get_ghostscript_path()
    
    try:
        subprocess.call([
            gs, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={quality[power]}',
            '-dNOPAUSE', '-dQUIET', '-dBATCH',
            f'-sOutputFile={output_file_path}',
            input_file_path
        ])
        return True
    except Exception as e:
        st.error(f"Erro ao comprimir o PDF: {str(e)}")
        return False

def alternative_compress_pdf(input_file_path, output_file_path):
    """
    Método alternativo de compressão usando apenas PyPDF2.
    É menos eficiente, mas não requer Ghostscript.
    """
    try:
        reader = PdfReader(input_file_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            # Adiciona cada página ao novo documento
            # Isso pode reduzir levemente o tamanho sem alterar muito a qualidade
            writer.add_page(page)
            
        # Salva o novo PDF
        with open(output_file_path, 'wb') as f:
            writer.write(f)
        return True
    except Exception as e:
        st.error(f"Erro ao comprimir o PDF: {str(e)}")
        return False

def is_ocrmypdf_installed():
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

def apply_ocrmypdf(input_path, output_path, language='por'):
    """
    Aplica OCR usando OCRmyPDF.
    
    :param input_path: Caminho para o arquivo PDF
    :param output_path: Caminho para salvar o PDF com OCR
    :param language: Idioma do texto (por = português, eng = inglês)
    :return: True se bem-sucedido, False caso contrário
    """
    try:
        # Criar cópia temporária para processar
        temp_input = input_path + ".tmp.pdf"
        shutil.copy2(input_path, temp_input)
        
        # Configurar argumentos do OCRmyPDF
        args = [
            'ocrmypdf',               # Comando
            '--force-ocr',            # Força OCR em todas as páginas (opção mais segura)
            '--optimize', '1',        # Otimizar pdf (usar 0-3)
            '--output-type', 'pdf',   # Saída como PDF
            '--jobs', '2',            # Número de processadores a usar
            '-l', language,           # Idioma
            temp_input,               # Arquivo de entrada
            output_path               # Arquivo de saída
        ]
        
        # Executar OCRmyPDF
        process = subprocess.run(
            args,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Limpar
        if os.path.exists(temp_input):
            os.unlink(temp_input)
            
        if process.returncode != 0:
            st.error(f"Erro no OCRmyPDF: {process.stderr}")
            return False
            
        return True
    except Exception as e:
        st.error(f"Erro ao executar OCRmyPDF: {str(e)}")
        return False

# Interface do Streamlit
st.title("Compressor de Arquivos PDF com OCR")
st.write("Upload um arquivo PDF para compactá-lo e torná-lo pesquisável (OCR).")

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Detalhes do arquivo original
    original_size_mb = uploaded_file.size / 1024 / 1024
    
    st.subheader("📄 Detalhes do arquivo")
    
    # Criando uma apresentação mais bonita com colunas e métricas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0;">Nome do arquivo</h4>
            <p style="font-size: 18px; font-weight: bold;">{uploaded_file.name}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric(
            label="Tamanho original",
            value=f"{original_size_mb:.2f} MB"
        )
    
    # Criando arquivos temporários para entrada e saída
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
        temp_input.write(uploaded_file.getvalue())
        input_path = temp_input.name
    
    output_path = input_path.replace('.pdf', '_comprimido.pdf')
    
    # Opções de compressão
    st.subheader("Opções de compressão")
    
    # Usando Ghostscript como método padrão, sem oferecer outras opções
    compression_method = "Ghostscript"
    
    # Ajuste do nível de compressão
    compression_level = st.slider(
        "Nível de compressão",
        min_value=0,
        max_value=4,
        value=3,
        help="0: Mínima compressão, alta qualidade. 4: Máxima compressão, qualidade inferior."
    )
    
    # Opções de OCR
    st.subheader("Opções de OCR")
    
    # Verificar se OCRmyPDF está disponível
    ocrmypdf_installed = is_ocrmypdf_installed()
    
    # Opção para aplicar OCR
    apply_ocr = st.checkbox(
        "Aplicar OCR (torna o PDF pesquisável)", 
        value=ocrmypdf_installed,
        disabled=not ocrmypdf_installed,
        help="Requer OCRmyPDF instalado"
    )
    
    # Aviso se OCRmyPDF não estiver instalado
    if not ocrmypdf_installed:
        st.warning("""
        ⚠️ **OCRmyPDF não detectado no seu sistema!**
        
        Para usar o OCR, instale o OCRmyPDF com:
        
        - Windows: `pip install ocrmypdf`
        - Mac: `brew install ocrmypdf`
        - Linux: `sudo apt-get install ocrmypdf`
        
        Depois da instalação, reinicie este aplicativo.
        """)
    
    # Usando português como idioma padrão fixo para OCR
    if apply_ocr:
        # Idioma fixo em português
        ocr_language = "por"
        
        st.info("""
        **Nota sobre OCR:**
        - O OCR torna o texto do PDF pesquisável, mesmo se for uma imagem escaneada
        - Pode aumentar ligeiramente o tamanho do arquivo
        - O idioma de reconhecimento está definido como português
        """)
    
    # Botão para comprimir
    if st.button("Comprimir PDF"):
        # Verificar disponibilidade do OCRmyPDF se OCR for selecionado
        if apply_ocr and not ocrmypdf_installed:
            st.error("OCRmyPDF não está disponível. O OCR será ignorado.")
            apply_ocr = False
        
        # Caminhos para arquivos temporários
        compressed_path = input_path.replace('.pdf', '_comprimido.pdf')
        final_output_path = input_path.replace('.pdf', '_final.pdf')
        
        with st.spinner('Processando o arquivo PDF...'):
            success = False
            
            # Etapa 1: Compressão
            st.text("Etapa 1/2: Comprimindo o PDF...")
            success = compress_pdf(input_path, compressed_path, compression_level)
            
            # Etapa 2: OCR (se selecionado e disponível)
            if success and apply_ocr:
                st.text("Etapa 2/2: Aplicando OCR para tornar o PDF pesquisável...")
                ocr_success = apply_ocrmypdf(compressed_path, final_output_path, ocr_language)
                
                # Se OCR foi bem-sucedido, use o arquivo final com OCR
                if ocr_success:
                    output_path = final_output_path
                # Caso contrário, continue com o arquivo apenas comprimido
                else:
                    output_path = compressed_path
                    st.warning("OCR falhou, mas a compressão foi aplicada com sucesso.")
            else:
                output_path = compressed_path
            
            if success:
                # Obtendo o tamanho do arquivo comprimido
                compressed_size = os.path.getsize(output_path) / 1024 / 1024  # em MB
                
                # Calculando a redução de tamanho
                size_reduction = (1 - (compressed_size / original_size_mb)) * 100
                
                # Exibir resultados de forma mais atraente
                st.success(f"✅ Compressão concluída com sucesso!")
                
                # Mostrar resultados em colunas com métricas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Tamanho original",
                        value=f"{original_size_mb:.2f} MB"
                    )
                
                with col2:
                    st.metric(
                        label="Tamanho após compressão",
                        value=f"{compressed_size:.2f} MB",
                        delta=f"-{size_reduction:.1f}%",
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        label="Economia de espaço",
                        value=f"{(original_size_mb - compressed_size):.2f} MB"
                    )
                
                # Adicionando uma barra de progresso visual para a redução
                st.markdown("##### Redução de tamanho:")
                st.progress(size_reduction / 100)
                
                # Opção para download com estilo melhorado
                st.markdown("### 📥 Download")
                
                with st.container():
                    st.markdown("""
                    <style>
                    div.stDownloadButton > button {
                        background-color: #4CAF50;
                        color: white;
                        padding: 12px 20px;
                        border: none;
                        border-radius: 4px;
                        font-size: 16px;
                        transition-duration: 0.4s;
                    }
                    div.stDownloadButton > button:hover {
                        background-color: #45a049;
                        box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    with open(output_path, "rb") as file:
                        download_filename = f"comprimido_{'ocr_' if apply_ocr else ''}{uploaded_file.name}"
                        download_btn = st.download_button(
                            label=f"📄 Baixar PDF {'com OCR ' if apply_ocr else ''}comprimido",
                            data=file,
                            file_name=download_filename,
                            mime="application/pdf",
                            on_click=lambda: setattr(st.session_state, 'download_clicked', True)
                        )
            else:
                st.error("Falha ao comprimir o arquivo PDF.")
        
        # Limpeza dos arquivos temporários
        try:
            os.unlink(input_path)
            if os.path.exists(compressed_path) and compressed_path != output_path:
                os.unlink(compressed_path)
            if os.path.exists(output_path) and not st.session_state.get('download_clicked', False):
                os.unlink(output_path)
        except:
            pass  # Ignora erros de limpeza

