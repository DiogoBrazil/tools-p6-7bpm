# tools-p-7bpm/pages/1_Ferramentas_PDF.py

import streamlit as st
from modules.pdf_transformer import PDFTransformer
import os
import tempfile
import io
import time
import shutil
import logging
# from PyPDF2 import PdfReader # REMOVIDO - Não é mais necessário aqui

# --- Constantes de Limite de Tamanho ---
# Limite máximo aumentado para 500 MB
MAX_SIZE_BYTES = 500 * 1024 * 1024
COMPRESS_MIN_SIZE_BYTES = 1 * 1024 * 1024 # 1 MB (Mínimo para compressão)
MAX_SIZE_MB = MAX_SIZE_BYTES / (1024 * 1024)
COMPRESS_MIN_SIZE_MB = COMPRESS_MIN_SIZE_BYTES / (1024 * 1024)

# --- Função de Validação ---
# Valida APENAS o tamanho MÁXIMO GERAL
def validate_file_size(uploaded_file, operation_type):
    if not uploaded_file: return False
    file_size = uploaded_file.size
    file_size_mb = file_size / (1024 * 1024)
    if file_size > MAX_SIZE_BYTES: # Usa o novo MAX_SIZE_BYTES (500MB)
        st.error(f"Arquivo muito grande ({file_size_mb:.1f} MB). O limite máximo é de {MAX_SIZE_MB:.0f} MB.")
        return False
    return True # Retorna True se estiver dentro do limite máximo

# --- Configuração da Página ---
st.set_page_config(
    page_title="Ferramentas PDF - 7ºBPM/P-6", page_icon="📄",
    layout="centered", initial_sidebar_state="collapsed"
)

# --- CSS Customizado (RESTAURADO) ---
st.write("""
<style>
    /* Esconde a sidebar */
    .css-1544g2n { display: none !important; }
    /* Ajusta o layout */
    .css-1d391kg, .block-container { max-width: 1000px; padding: 1rem; margin: 0 auto; }
    /* Container Botão Voltar */
    div.element-container:nth-child(1) { margin-top: 1rem; }
    /* Estilo Botão Voltar */
    div.element-container:nth-child(1) > .stButton > button {
        background-color: #f0f2f6 !important; color: #333 !important;
        border: 1px solid #d1d1d1 !important; font-weight: normal !important;
        box-shadow: none !important;
    }
    div.element-container:nth-child(1) > .stButton > button:hover {
        background-color: #e0e2e6 !important; color: #111 !important;
        border-color: #c1c1c1 !important; box-shadow: none !important;
    }
    /* Cabeçalho */
    .header-container { display: flex; align-items: center; margin-bottom: 20px; }
    .header-icon { font-size: 2.5em; margin-right: 15px; }
    /* Botões de Ação */
    .stButton > button {
        background-color: #2196F3; color: white; padding: 12px 20px; border: none;
        border-radius: 4px; font-size: 16px; transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #0b7dda; box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    /* Botão de Download */
    div.stDownloadButton > button {
        background-color: #4CAF50; color: white; padding: 12px 20px; border: none;
        border-radius: 4px; font-size: 16px; transition: all 0.3s;
    }
    div.stDownloadButton > button:hover {
        background-color: #45a049; box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    /* Métricas de Compressão */
    .compress-metrics .stMetric { background-color: #f8f9fa; border-radius: 5px; padding: 10px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- Navegação e Cabeçalho ---
if st.button("← Voltar à página inicial", key="back_button_pdf_tools"):
    st.switch_page("Home.py")

st.markdown("""
<div class="header-container">
    <div class="header-icon">📄</div>
    <div>
        <h1>Ferramentas PDF</h1>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("Selecione a operação desejada e faça upload dos arquivos.")

# --- Inicialização e Seleção ---
pdf_processor = PDFTransformer()

operation_type = st.selectbox(
    "Escolha a operação PDF:",
    (
        "Selecione...",
        "Comprimir PDF",
        "Tornar PDF Pesquisável (OCR)",
        "Juntar PDFs",
        "Imagens para PDF",
        "PDF para DOCX",
        "PDF para Imagens (PNG)",
        "Documento (DOCX, DOC, ODT, TXT) para PDF",
        "Planilha (XLSX, CSV, ODS) para PDF"
    ),
    key="operation_select"
)

# --- Lógica e UI (com limites atualizados) ---
uploaded_file = None
uploaded_files = []
output_file_data = None
output_filename = "resultado"
output_mimetype = "application/octet-stream"
processing_triggered = False
temp_dir_path = None

upload_placeholder = st.empty()
options_placeholder = st.empty()
button_placeholder = st.empty()
result_placeholder = st.empty()

try:
    # --- COMPRESS PDF ---
    if operation_type == "Comprimir PDF":
        with upload_placeholder.container():
            uploaded_file = st.file_uploader(
                f"Carregue um PDF (Mín: {COMPRESS_MIN_SIZE_MB:.0f} MB, Máx: {MAX_SIZE_MB:.0f} MB)",
                type="pdf", key="pdf_upload_compress"
            )
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            # Verificação RÍGIDA do tamanho MÍNIMO
            if uploaded_file.size < COMPRESS_MIN_SIZE_BYTES:
                 options_placeholder.error(f"Arquivo muito pequeno ({file_size_mb:.1f} MB). A compressão só é permitida para arquivos com mais de {COMPRESS_MIN_SIZE_MB:.0f} MB.")
            else:
                # Verifica o tamanho MÁXIMO
                if validate_file_size(uploaded_file, operation_type): # Verifica MAX_SIZE_BYTES (500MB)
                    with options_placeholder.container():
                        compression_level = st.slider(
                            "Nível de compressão (0=Menor, 4=Maior)", 0, 4, 3, key="compress_level",
                            help="0: Qualidade alta, menor compressão. 4: Qualidade baixa, maior compressão."
                        )
                    processing_triggered = button_placeholder.button(
                        "Comprimir PDF", key="compress_btn", use_container_width=True,
                        disabled=not pdf_processor.gs_available
                    )
                    if not pdf_processor.gs_available: options_placeholder.error("❌ Ghostscript não detectado. Compressão indisponível.")

                    if processing_triggered and pdf_processor.gs_available:
                        pdf_bytes = uploaded_file.getvalue()
                        with result_placeholder, st.spinner(f"Comprimindo PDF (Nível {compression_level})..."):
                            # ... (lógica de compressão e métricas) ...
                            success, processed_bytes, original_size, final_size = pdf_processor.process_compression_ocr(
                                pdf_bytes, compression_level=compression_level, apply_ocr=False
                            )
                            if success and processed_bytes:
                                st.success("✅ PDF comprimido com sucesso!")
                                output_filename = f"comprimido_{uploaded_file.name}"
                                output_mimetype = "application/pdf"; output_file_data = processed_bytes
                                reduction_percent = (1 - (final_size / original_size)) * 100 if original_size > 0 else 0
                                st.markdown('<div class="compress-metrics">', unsafe_allow_html=True)
                                cols = st.columns(3)
                                with cols[0]: st.metric("Tam. Original", f"{original_size:.2f} MB")
                                with cols[1]: st.metric("Tam. Final", f"{final_size:.2f} MB", f"-{reduction_percent:.1f}%" if reduction_percent >= 0.1 else None, delta_color="inverse")
                                with cols[2]: st.metric("Economia", f"{(original_size - final_size):.2f} MB")
                                st.progress(min(reduction_percent / 100, 1.0))
                                st.markdown('</div>', unsafe_allow_html=True)
                            else: st.error("❌ Falha ao comprimir o PDF.")

    # --- OCR ---
    elif operation_type == "Tornar PDF Pesquisável (OCR)":
        with upload_placeholder.container():
            uploaded_file = st.file_uploader(
                f"Carregue um PDF (Máx: {MAX_SIZE_MB:.0f} MB)", type="pdf", key="pdf_upload_ocr"
            )
        if uploaded_file:
            if validate_file_size(uploaded_file, operation_type):
                 processing_triggered = button_placeholder.button(
                     "Aplicar OCR", key="ocr_btn", use_container_width=True,
                     disabled=not pdf_processor.ocrmypdf_installed
                 )
                 if not pdf_processor.ocrmypdf_installed: options_placeholder.error("❌ OCRmyPDF não detectado. Função indisponível.")
            if processing_triggered and pdf_processor.ocrmypdf_installed:
                 # ... (lógica OCR) ...
                 pdf_bytes = uploaded_file.getvalue()
                 with result_placeholder, st.spinner("Aplicando OCR ao PDF... Isso pode demorar."):
                     success, processed_bytes, original_size, final_size = pdf_processor.process_compression_ocr(
                         pdf_bytes, compression_level=-1, apply_ocr=True, ocr_language='por'
                     )
                     if success and processed_bytes:
                         st.success("✅ OCR aplicado com sucesso! O PDF agora é pesquisável.")
                         output_filename = f"ocr_{uploaded_file.name}"
                         output_mimetype = "application/pdf"; output_file_data = processed_bytes
                         st.info(f"Tamanho original: {original_size:.2f} MB | Tamanho final: {final_size:.2f} MB")
                     else: st.error("❌ Falha ao aplicar OCR no PDF.")

    # --- JUNTAR PDFs ---
    elif operation_type == "Juntar PDFs":
        with upload_placeholder.container():
            uploaded_files = st.file_uploader(
                f"Carregue 2 ou mais arquivos PDF para juntar (Total Máx: {MAX_SIZE_MB:.0f} MB)",
                type="pdf", accept_multiple_files=True, key="pdf_upload_merge"
            )
        if uploaded_files and len(uploaded_files) >= 2:
            total_size = sum(f.size for f in uploaded_files)
            if total_size > MAX_SIZE_BYTES:
                st.error(f"Tamanho total ({total_size / (1024*1024):.1f} MB) excede o limite de {MAX_SIZE_MB:.0f} MB.")
            else:
                 with options_placeholder.container():
                    # ... (lógica de ordenação) ...
                    st.write("**Ordem de Junção:**")
                    ordered_files = sorted(uploaded_files, key=lambda f: f.name)
                    st.caption("Atenção: A ordem final será alfabética pelo nome do arquivo.")
                    for i, f in enumerate(ordered_files):
                         st.write(f"{i+1}. {f.name} ({f.size / 1024 / 1024:.1f} MB)")
                 processing_triggered = button_placeholder.button("Juntar PDFs", key="merge_btn", use_container_width=True)

            if processing_triggered and total_size <= MAX_SIZE_BYTES:
                 # ... (lógica de merge) ...
                pdf_byte_streams = [file.getvalue() for file in ordered_files]
                with result_placeholder, st.spinner(f"Juntando {len(pdf_byte_streams)} PDFs..."):
                    success, result_bytes, message = pdf_processor.merge_pdfs(pdf_byte_streams)
                    if success and result_bytes:
                        st.success(f"✅ {message}")
                        output_filename = f"pdf_juntado_{int(time.time())}.pdf"
                        output_mimetype = "application/pdf"; output_file_data = result_bytes
                    else: st.error(f"❌ Falha ao juntar PDFs: {message}")
        elif uploaded_files and len(uploaded_files) < 2:
            options_placeholder.warning("Selecione pelo menos 2 arquivos PDF para juntar.")


    # --- IMAGES TO PDF ---
    elif operation_type == "Imagens para PDF":
        with upload_placeholder.container():
            uploaded_files = st.file_uploader(
                f"Carregue imagens (JPG, PNG, JPEG) (Total Máx: {MAX_SIZE_MB:.0f} MB)",
                type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_upload"
            )
        if uploaded_files:
            total_size = sum(f.size for f in uploaded_files)
            if total_size > MAX_SIZE_BYTES:
                 st.error(f"Tamanho total ({total_size / (1024*1024):.1f} MB) excede o limite de {MAX_SIZE_MB:.0f} MB.")
            else:
                processing_triggered = button_placeholder.button("Converter Imagens para PDF", key="img_to_pdf_btn", use_container_width=True)
            if processing_triggered and total_size <= MAX_SIZE_BYTES:
                # ... (lógica de conversão de imagem) ...
                 with result_placeholder, st.spinner("Convertendo imagens para PDF..."):
                    image_bytes_list = [file.getvalue() for file in uploaded_files]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
                        output_pdf_path = temp_pdf_file.name
                    try:
                        success = pdf_processor.image_to_pdf(image_bytes_list, output_pdf_path)
                        if success and os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                            st.success("✅ Imagens convertidas para PDF!")
                            output_filename = f"imagens_convertidas_{int(time.time())}.pdf"
                            output_mimetype = "application/pdf";
                            with open(output_pdf_path, "rb") as f: output_file_data = f.read()
                        else: st.error("❌ Falha ao converter imagens.")
                    finally:
                        if os.path.exists(output_pdf_path): os.unlink(output_pdf_path)


    # --- PDF TO DOCX ---
    elif operation_type == "PDF para DOCX":
        with upload_placeholder.container():
            uploaded_file = st.file_uploader(f"Carregue PDF (Máx: {MAX_SIZE_MB:.0f} MB)", type="pdf", key="pdf_upload_docx")
        if uploaded_file:
            if validate_file_size(uploaded_file, operation_type):
                 # ... (checkbox OCR, botão) ...
                 with options_placeholder.container():
                     apply_ocr_docx = st.checkbox("Tentar OCR (PDFs baseados em imagem)", key="ocr_checkbox_docx", value=False, help="Útil se o PDF for apenas uma imagem escaneada, sem texto selecionável.", disabled=not pdf_processor.ocrmypdf_installed)
                     if not pdf_processor.ocrmypdf_installed: st.warning("⚠️ OCRmyPDF não detectado. Opção de OCR desabilitada.")
                 processing_triggered = button_placeholder.button("Converter PDF para DOCX", key="pdf_to_docx_btn", use_container_width=True)
            if processing_triggered:
                 # ... (lógica de conversão pdf->docx) ...
                 pdf_bytes = uploaded_file.getvalue()
                 with result_placeholder, st.spinner(f"Convertendo PDF para DOCX{' com tentativa de OCR' if apply_ocr_docx else ''}..."):
                      with tempfile.TemporaryDirectory() as temp_proc_dir:
                           input_pdf_path = os.path.join(temp_proc_dir, uploaded_file.name)
                           base_name = os.path.splitext(uploaded_file.name)[0]
                           output_docx_path = os.path.join(temp_proc_dir, f"{base_name}_{int(time.time())}.docx")
                           with open(input_pdf_path, "wb") as f: f.write(pdf_bytes)
                           success = pdf_processor.pdf_to_docx(input_pdf_path, output_docx_path, apply_ocr=apply_ocr_docx)
                           if success and os.path.exists(output_docx_path) and os.path.getsize(output_docx_path) > 100:
                                st.success(f"✅ PDF convertido para DOCX!")
                                output_filename = f"{base_name}.docx"
                                output_mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                with open(output_docx_path, "rb") as f: output_file_data = f.read()
                           elif success:
                                st.warning("⚠️ Conversão concluída, mas o arquivo DOCX parece vazio ou muito pequeno. O PDF original pode não conter texto extraível.")
                           else: st.error("❌ Falha ao converter para DOCX.")


    # --- PDF TO IMAGES (PNG) ---
    elif operation_type == "PDF para Imagens (PNG)":
        with upload_placeholder.container():
             uploaded_file = st.file_uploader(f"Carregue PDF (Máx: {MAX_SIZE_MB:.0f} MB)", type="pdf", key="pdf_upload_img")
        if uploaded_file:
             if validate_file_size(uploaded_file, operation_type):
                 processing_triggered = button_placeholder.button("Converter PDF para Imagens", key="pdf_to_img_btn", use_container_width=True)
             if processing_triggered:
                 # ... (lógica pdf->img) ...
                  pdf_bytes = uploaded_file.getvalue()
                  with result_placeholder, st.spinner("Convertendo PDF para imagens PNG..."):
                       with tempfile.TemporaryDirectory() as temp_img_dir:
                           input_pdf_path = os.path.join(temp_img_dir, "input.pdf");
                           with open(input_pdf_path, "wb") as f: f.write(pdf_bytes)
                           image_paths = pdf_processor.pdf_to_image(input_pdf_path, temp_img_dir, image_format='png')
                           if image_paths:
                                zip_path = os.path.join(temp_img_dir, "pdf_imagens.zip")
                                zip_success = pdf_processor.create_zip_from_files(image_paths, zip_path)
                                if zip_success and os.path.exists(zip_path):
                                     st.success(f"✅ PDF convertido para {len(image_paths)} imagem(ns) PNG!")
                                     output_filename = f"{os.path.splitext(uploaded_file.name)[0]}_imgs.zip"
                                     output_mimetype = "application/zip";
                                     with open(zip_path, "rb") as f: output_file_data = f.read()
                                else: st.error("❌ Falha ao criar arquivo ZIP com as imagens.")
                           else: st.error("❌ Falha ao converter PDF para imagens.")


    # --- DOCUMENT TO PDF ---
    elif operation_type == "Documento (DOCX, DOC, ODT, TXT) para PDF":
        with upload_placeholder.container():
             allowed_doc_types = ["docx", "doc", "odt", "txt"]
             uploaded_file = st.file_uploader(f"Carregue documento ({', '.join(allowed_doc_types).upper()}) (Máx: {MAX_SIZE_MB:.0f} MB)", type=allowed_doc_types, key="doc_upload")
        if uploaded_file:
             if validate_file_size(uploaded_file, operation_type):
                 # ... (verificação LO, botão) ...
                  with options_placeholder.container():
                       if not pdf_processor.libreoffice_path: st.error("❌ LibreOffice não encontrado. Conversão indisponível.")
                       else: st.info(f"ℹ️ Usando LibreOffice ({pdf_processor.libreoffice_path}). A conversão pode levar alguns segundos.")
                  processing_triggered = button_placeholder.button(f"Converter {uploaded_file.name} para PDF", key="doc_to_pdf_btn", use_container_width=True, disabled=not pdf_processor.libreoffice_path)
             if processing_triggered and pdf_processor.libreoffice_path:
                 # ... (lógica doc->pdf) ...
                  doc_bytes = uploaded_file.getvalue()
                  with result_placeholder, st.spinner(f"Convertendo {uploaded_file.name} para PDF usando LibreOffice..."):
                       with tempfile.TemporaryDirectory() as temp_conv_dir:
                            input_doc_path = os.path.join(temp_conv_dir, uploaded_file.name)
                            output_pdf_path = os.path.join(temp_conv_dir, f"{os.path.splitext(uploaded_file.name)[0]}.pdf")
                            with open(input_doc_path, "wb") as f: f.write(doc_bytes)
                            success = pdf_processor.document_to_pdf(input_doc_path, output_pdf_path)
                            if success and os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                                 st.success(f"✅ Documento convertido para PDF!")
                                 output_filename = f"{os.path.splitext(uploaded_file.name)[0]}.pdf"
                                 output_mimetype = "application/pdf";
                                 with open(output_pdf_path, "rb") as f: output_file_data = f.read()
                            else: st.error("❌ Falha ao converter documento para PDF via LibreOffice.")


    # --- PLANILHA PARA PDF ---
    elif operation_type == "Planilha (XLSX, CSV, ODS) para PDF":
        with upload_placeholder.container():
             allowed_sheet_types = ["xlsx", "csv", "ods"]
             uploaded_file = st.file_uploader(
                 f"Carregue planilha ({', '.join(allowed_sheet_types).upper()}) (Máx: {MAX_SIZE_MB:.0f} MB)",
                 type=allowed_sheet_types,
                 key="sheet_upload"
             )
        if uploaded_file:
             if validate_file_size(uploaded_file, operation_type):
                 # ... (verificação LO, botão) ...
                  with options_placeholder.container():
                       if not pdf_processor.libreoffice_path:
                            st.error("❌ LibreOffice não encontrado. Conversão de planilha indisponível.")
                       else:
                            st.info(f"ℹ️ Usando LibreOffice ({pdf_processor.libreoffice_path}). A conversão pode levar alguns segundos.")
                            st.caption("Nota: A formatação pode variar. Múltiplas abas podem ser convertidas em múltiplas páginas PDF.")
                  processing_triggered = button_placeholder.button(
                      f"Converter {uploaded_file.name} para PDF",
                      key="sheet_to_pdf_btn",
                      use_container_width=True,
                      disabled=not pdf_processor.libreoffice_path
                  )
             if processing_triggered and pdf_processor.libreoffice_path:
                 # ... (lógica sheet->pdf) ...
                  sheet_bytes = uploaded_file.getvalue()
                  with result_placeholder, st.spinner(f"Convertendo planilha {uploaded_file.name} para PDF usando LibreOffice..."):
                       with tempfile.TemporaryDirectory() as temp_conv_dir:
                            input_sheet_path = os.path.join(temp_conv_dir, uploaded_file.name)
                            output_pdf_path = os.path.join(temp_conv_dir, f"{os.path.splitext(uploaded_file.name)[0]}.pdf")
                            with open(input_sheet_path, "wb") as f: f.write(sheet_bytes)
                            success = pdf_processor.document_to_pdf(input_sheet_path, output_pdf_path)
                            if success and os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                                 st.success(f"✅ Planilha convertida para PDF!")
                                 output_filename = f"{os.path.splitext(uploaded_file.name)[0]}.pdf"
                                 output_mimetype = "application/pdf";
                                 with open(output_pdf_path, "rb") as f: output_file_data = f.read()
                            else:
                                 st.error("❌ Falha ao converter planilha para PDF via LibreOffice.")
                                 if uploaded_file.name.lower().endswith('.csv'):
                                     st.info("Dica para CSV: Verifique se o arquivo CSV está formatado corretamente (delimitadores, codificação).")


    # --- Download Button ---
    if output_file_data:
        result_placeholder.empty()
        button_placeholder.download_button(
            label=f"📄 Baixar {output_filename}", data=output_file_data,
            file_name=output_filename, mime=output_mimetype,
            key="download_button", use_container_width=True
        )

finally:
    # --- Limpeza Final ---
    if temp_dir_path and os.path.exists(temp_dir_path):
        try:
            shutil.rmtree(temp_dir_path)
            logging.info(f"Diretório temporário manual {temp_dir_path} removido.")
        except Exception as e:
            logging.warning(f"Erro ao remover diretório temporário manual {temp_dir_path}: {e}")

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e6e6e6; text-align: center; font-size: 0.9rem; color: #666;">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
