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
MAX_SIZE_BYTES = 200 * 1024 * 1024
COMPRESS_MIN_SIZE_BYTES = 1 * 1024 * 1024
MAX_SIZE_MB = MAX_SIZE_BYTES / (1024 * 1024)
COMPRESS_MIN_SIZE_MB = COMPRESS_MIN_SIZE_BYTES / (1024 * 1024)

# --- Função de Validação ---
def validate_file_size(uploaded_file, operation_type):
    if not uploaded_file: return False
    file_size = uploaded_file.size
    file_size_mb = file_size / (1024 * 1024)
    if file_size > MAX_SIZE_BYTES:
        st.error(f"Arquivo muito grande ({file_size_mb:.1f} MB). O limite máximo é de {MAX_SIZE_MB:.0f} MB.")
        return False
    if operation_type == "Comprimir PDF" and file_size < COMPRESS_MIN_SIZE_BYTES:
        st.error(f"Arquivo muito pequeno ({file_size_mb:.1f} MB). A compressão requer no mínimo {COMPRESS_MIN_SIZE_MB:.0f} MB.")
        return False
    return True

# --- Configuração da Página ---
st.set_page_config(
    page_title="Ferramentas PDF - 7ºBPM/P-6", page_icon="📄",
    layout="centered", initial_sidebar_state="collapsed"
)

# --- CSS Customizado ---
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

# Opção "Organizar Páginas PDF" removida
operation_type = st.selectbox(
    "Escolha a operação PDF:",
    (
        "Selecione...",
        "Comprimir PDF",
        "Tornar PDF Pesquisável (OCR)",
        "Juntar PDFs",
        # "Organizar Páginas PDF", # <<< REMOVIDO
        "Imagens para PDF",
        "PDF para DOCX",
        "PDF para Imagens (PNG)",
        "Documento (DOCX, DOC, ODT, TXT) para PDF"
    ),
    key="operation_select"
)

# --- Lógica e UI ---
uploaded_file = None
uploaded_files = []
output_file_data = None
output_filename = "resultado"
output_mimetype = "application/octet-stream"
processing_triggered = False
temp_dir = None

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
            if validate_file_size(uploaded_file, operation_type):
                with options_placeholder.container():
                    compression_level = st.slider(
                        "Nível de compressão (0=Menor, 4=Maior)", 0, 4, 3, key="compress_level",
                        help="0: Qualidade alta, menor compressão. 4: Qualidade baixa, maior compressão."
                    )
                processing_triggered = button_placeholder.button(
                    "Comprimir PDF", key="compress_btn", use_container_width=True,
                    disabled=not pdf_processor.gs_available
                )
                if not pdf_processor.gs_available: options_placeholder.warning("Ghostscript não detectado.")
            if processing_triggered and pdf_processor.gs_available:
                pdf_bytes = uploaded_file.getvalue()
                with result_placeholder, st.spinner(f"Comprimindo PDF (Nível {compression_level})..."):
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
                 if not pdf_processor.ocrmypdf_installed: options_placeholder.warning("OCRmyPDF não detectado.")
            if processing_triggered and pdf_processor.ocrmypdf_installed:
                 pdf_bytes = uploaded_file.getvalue()
                 with result_placeholder, st.spinner("Aplicando OCR ao PDF..."):
                     success, processed_bytes, original_size, final_size = pdf_processor.process_compression_ocr(
                         pdf_bytes, compression_level=-1, apply_ocr=True, ocr_language='por' # Comp level -1 para não comprimir
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
            if total_size > MAX_SIZE_BYTES: st.error(f"Tamanho total excede {MAX_SIZE_MB:.0f} MB.")
            else:
                with options_placeholder.container():
                    st.write("**Ordem de Junção:**")
                    for i, f in enumerate(uploaded_files): st.write(f"{i+1}. {f.name} ({f.size / 1024 / 1024:.1f} MB)")
                    st.caption("A ordem é baseada na sequência de upload.")
                processing_triggered = button_placeholder.button("Juntar PDFs", key="merge_btn", use_container_width=True)
            if processing_triggered and total_size <= MAX_SIZE_BYTES:
                pdf_byte_streams = [file.getvalue() for file in uploaded_files]
                with result_placeholder, st.spinner(f"Juntando {len(pdf_byte_streams)} PDFs..."):
                    success, result_bytes, message = pdf_processor.merge_pdfs(pdf_byte_streams)
                    if success and result_bytes:
                        st.success(f"✅ {message}")
                        output_filename = f"pdf_juntado_{int(time.time())}.pdf"
                        output_mimetype = "application/pdf"; output_file_data = result_bytes
                    else: st.error(f"❌ Falha ao juntar PDFs: {message}")
        elif uploaded_files and len(uploaded_files) < 2:
            options_placeholder.warning("Selecione pelo menos 2 arquivos PDF para juntar.")

    # --- Bloco "Organizar Páginas PDF" REMOVIDO ---

    # --- IMAGES TO PDF ---
    elif operation_type == "Imagens para PDF":
        with upload_placeholder.container():
            uploaded_files = st.file_uploader(
                f"Carregue imagens (JPG, PNG, JPEG) (Total Máx: {MAX_SIZE_MB:.0f} MB)",
                type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_upload"
            )
        if uploaded_files:
            total_size = sum(f.size for f in uploaded_files)
            if total_size > MAX_SIZE_BYTES: st.error(f"Tamanho total excede {MAX_SIZE_MB:.0f} MB.")
            else: processing_triggered = button_placeholder.button("Converter Imagens para PDF", key="img_to_pdf_btn", use_container_width=True)
            if processing_triggered and total_size <= MAX_SIZE_BYTES:
                with result_placeholder, st.spinner("Convertendo imagens para PDF..."):
                    image_bytes_list = [file.getvalue() for file in uploaded_files]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf: output_pdf_path = temp_pdf.name
                    success = pdf_processor.image_to_pdf(image_bytes_list, output_pdf_path)
                    if success and os.path.exists(output_pdf_path):
                        st.success("✅ Imagens convertidas para PDF!")
                        output_filename = f"imagens_convertidas_{int(time.time())}.pdf"
                        output_mimetype = "application/pdf";
                        with open(output_pdf_path, "rb") as f: output_file_data = f.read()
                    else: st.error("❌ Falha ao converter imagens.")
                    if os.path.exists(output_pdf_path): os.unlink(output_pdf_path)

    # --- PDF TO DOCX ---
    elif operation_type == "PDF para DOCX":
        with upload_placeholder.container():
            uploaded_file = st.file_uploader(f"Carregue PDF (Máx: {MAX_SIZE_MB:.0f} MB)", type="pdf", key="pdf_upload_docx")
        if uploaded_file:
            if validate_file_size(uploaded_file, operation_type):
                 with options_placeholder.container():
                     apply_ocr_docx = st.checkbox("Aplicar OCR (PDFs imagem)", key="ocr_checkbox_docx", value=False, disabled=not pdf_processor.ocrmypdf_installed)
                     if not pdf_processor.ocrmypdf_installed: st.warning("OCRmyPDF não detectado.")
                 processing_triggered = button_placeholder.button("Converter PDF para DOCX", key="pdf_to_docx_btn", use_container_width=True)
            if processing_triggered:
                 pdf_bytes = uploaded_file.getvalue()
                 with result_placeholder, st.spinner(f"Convertendo PDF para DOCX{' com OCR' if apply_ocr_docx else ''}..."):
                      with tempfile.TemporaryDirectory() as temp_proc_dir:
                           input_pdf_path = os.path.join(temp_proc_dir, uploaded_file.name)
                           output_docx_path = os.path.join(temp_proc_dir, f"{os.path.splitext(uploaded_file.name)[0]}.docx")
                           with open(input_pdf_path, "wb") as f: f.write(pdf_bytes)
                           success = pdf_processor.pdf_to_docx(input_pdf_path, output_docx_path, apply_ocr=apply_ocr_docx)
                           if success and os.path.exists(output_docx_path):
                                st.success(f"✅ PDF convertido para DOCX!")
                                output_filename = f"{os.path.splitext(uploaded_file.name)[0]}.docx"
                                output_mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                with open(output_docx_path, "rb") as f: output_file_data = f.read()
                           else: st.error("❌ Falha ao converter para DOCX.")

    # --- PDF TO IMAGES (PNG) ---
    elif operation_type == "PDF para Imagens (PNG)":
        with upload_placeholder.container():
             uploaded_file = st.file_uploader(f"Carregue PDF (Máx: {MAX_SIZE_MB:.0f} MB)", type="pdf", key="pdf_upload_img")
        if uploaded_file:
             if validate_file_size(uploaded_file, operation_type): processing_triggered = button_placeholder.button("Converter PDF para Imagens", key="pdf_to_img_btn", use_container_width=True)
             if processing_triggered:
                  pdf_bytes = uploaded_file.getvalue()
                  with result_placeholder, st.spinner("Convertendo PDF para imagens PNG..."):
                       temp_dir = tempfile.mkdtemp()
                       input_pdf_path = os.path.join(temp_dir, "input.pdf");
                       with open(input_pdf_path, "wb") as f: f.write(pdf_bytes)
                       image_paths = pdf_processor.pdf_to_image(input_pdf_path, temp_dir, image_format='png')
                       if image_paths:
                            zip_path = os.path.join(temp_dir, "pdf_imagens.zip")
                            zip_success = pdf_processor.create_zip_from_files(image_paths, zip_path)
                            if zip_success and os.path.exists(zip_path):
                                 st.success(f"✅ PDF convertido para {len(image_paths)} imagem(ns) PNG!")
                                 output_filename = f"{os.path.splitext(uploaded_file.name)[0]}_imgs.zip"
                                 output_mimetype = "application/zip";
                                 with open(zip_path, "rb") as f: output_file_data = f.read()
                            else: st.error("❌ Falha ao criar ZIP.")
                       else: st.error("❌ Falha ao converter para imagens.")

    # --- DOCUMENT TO PDF ---
    elif operation_type == "Documento (DOCX, DOC, ODT, TXT) para PDF":
        with upload_placeholder.container():
             uploaded_file = st.file_uploader(f"Carregue documento (Máx: {MAX_SIZE_MB:.0f} MB)", type=["docx", "doc", "odt", "txt"], key="doc_upload")
        if uploaded_file:
             if validate_file_size(uploaded_file, operation_type):
                  with options_placeholder.container():
                       if not pdf_processor.libreoffice_path: st.error("❌ LibreOffice não encontrado.")
                       else: st.info(f"ℹ️ Usando LibreOffice ({pdf_processor.libreoffice_path}).")
                  processing_triggered = button_placeholder.button(f"Converter {uploaded_file.name} para PDF", key="doc_to_pdf_btn", use_container_width=True, disabled=not pdf_processor.libreoffice_path)
             if processing_triggered:
                  doc_bytes = uploaded_file.getvalue()
                  with result_placeholder, st.spinner(f"Convertendo {uploaded_file.name} para PDF..."):
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
                            else: st.error("❌ Falha ao converter documento.")

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
    if temp_dir and os.path.exists(temp_dir):
        try: shutil.rmtree(temp_dir); logging.info(f"Dir temp {temp_dir} removido.")
        except Exception as e: logging.warning(f"Erro ao remover dir temp {temp_dir}: {e}")

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e6e6e6; text-align: center; font-size: 0.9rem; color: #666;">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
