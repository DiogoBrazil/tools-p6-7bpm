import os
import tempfile
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Inches
import img2pdf
from PIL import Image
import zipfile
import io # Para trabalhar com bytes em memória
import subprocess
import platform
import shutil
import logging
from PyPDF2 import PdfReader, PdfWriter # Import mantido para merge_pdfs

logging.basicConfig(level=logging.INFO)

class PDFTransformer:
    def __init__(self):
        self.ocrmypdf_cmd = 'ocrmypdf'
        self.ocrmypdf_installed = self._check_ocrmypdf_installed()
        self.libreoffice_path = self._find_libreoffice()
        self.gs_cmd = 'gswin64c' if platform.system() == 'Windows' else 'gs'
        self.gs_available = self._check_gs_available()

    def _check_ocrmypdf_installed(self):
        try:
            subprocess.run([self.ocrmypdf_cmd, '--version'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=True, text=True, timeout=5)
            logging.info("OCRmyPDF detectado.")
            return True
        except (subprocess.SubprocessError, FileNotFoundError, Exception) as e:
            logging.warning(f"OCRmyPDF não detectado ou erro ao verificar: {e}")
            return False

    def _apply_ocrmypdf(self, input_path, output_path, language='por'):
         if not self.ocrmypdf_installed:
             logging.error("Tentativa de usar OCRmyPDF, mas não está instalado.")
             return False
         with tempfile.TemporaryDirectory() as temp_ocr_dir:
             temp_input = os.path.join(temp_ocr_dir, "input_ocr.pdf")
             shutil.copy2(input_path, temp_input)
             temp_output = os.path.join(temp_ocr_dir, "output_ocr.pdf")
             args = [
                 self.ocrmypdf_cmd, '--force-ocr', '--optimize', '1', '--output-type', 'pdf',
                 '--jobs', '2', '-l', language, temp_input, temp_output
             ]
             try:
                 process = subprocess.run(args, capture_output=True, text=True, check=False, timeout=300)
                 if process.returncode != 0:
                     logging.error(f"Erro no OCRmyPDF (código {process.returncode}):")
                     logging.error(f"Stderr: {process.stderr}")
                     logging.error(f"Stdout: {process.stdout}")
                     return False
                 if os.path.exists(temp_output):
                     shutil.move(temp_output, output_path)
                     logging.info(f"OCR aplicado com sucesso e salvo em {output_path}")
                     return True
                 else:
                     logging.error("OCRmyPDF terminou sem erros, mas o arquivo de saída não foi encontrado.")
                     return False
             except subprocess.TimeoutExpired:
                  logging.error("OCRmyPDF excedeu o tempo limite.")
                  return False
             except Exception as e:
                  logging.error(f"Erro ao executar OCRmyPDF: {str(e)}")
                  return False

    def _find_libreoffice(self):
        for cmd in ['soffice', 'libreoffice']:
            try:
                subprocess.run([cmd, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
                logging.info(f"LibreOffice detectado usando o comando: '{cmd}'")
                return cmd
            except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
        logging.warning("Comando do LibreOffice ('soffice' ou 'libreoffice') não encontrado no PATH.")
        return None

    def _check_gs_available(self):
        try:
            subprocess.run([self.gs_cmd, '--version'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=True, text=True, timeout=5)
            logging.info(f"Ghostscript detectado usando o comando: '{self.gs_cmd}'")
            return True
        except (subprocess.SubprocessError, FileNotFoundError, Exception) as e:
            logging.warning(f"Ghostscript ({self.gs_cmd}) não detectado ou erro: {e}")
            return False

    def _compress_pdf_gs(self, input_file_path, output_file_path, power=3):
        if not self.gs_available:
            logging.error("Ghostscript não está disponível. Não é possível comprimir.")
            return False
        quality = {0: '/default', 1: '/prepress', 2: '/printer', 3: '/ebook', 4: '/screen'}
        power = max(0, min(4, power))
        command = [
            self.gs_cmd, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={quality[power]}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
            f'-sOutputFile={output_file_path}', input_file_path
        ]
        logging.info(f"Executando compressão Ghostscript: {' '.join(command)}")
        try:
            process = subprocess.run(command, capture_output=True, check=False, text=True, timeout=300)
            if process.returncode != 0:
                 logging.error(f"Erro no Ghostscript (código {process.returncode}):\nStderr: {process.stderr}\nStdout: {process.stdout}")
                 if os.path.exists(output_file_path): os.unlink(output_file_path)
                 return False
            if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
                logging.info("Compressão com Ghostscript concluída com sucesso.")
                return True
            else:
                logging.error("Ghostscript finalizou sem erro, mas o arquivo de saída não foi criado ou está vazio.")
                return False
        except subprocess.TimeoutExpired:
             logging.error("Compressão com Ghostscript excedeu o tempo limite.")
             if os.path.exists(output_file_path): os.unlink(output_file_path)
             return False
        except Exception as e:
            logging.error(f"Erro inesperado ao executar Ghostscript: {str(e)}")
            if os.path.exists(output_file_path): os.unlink(output_file_path)
            return False

    def process_compression_ocr(self, file_bytes, compression_level=3, apply_ocr=False, ocr_language='por'):
        original_size_mb = len(file_bytes) / 1024 / 1024
        processed_bytes = None; final_size_mb = 0; success = False
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.pdf")
            with open(input_path, "wb") as f: f.write(file_bytes)
            current_step_output = input_path; step_successful = True
            if compression_level >= 0:
                logging.info(f"Iniciando Etapa de Compressão (Nível {compression_level})...")
                compressed_path = os.path.join(temp_dir, "compressed.pdf")
                step_successful = self._compress_pdf_gs(current_step_output, compressed_path, compression_level)
                if step_successful: current_step_output = compressed_path; logging.info("Compressão bem-sucedida.")
                else: logging.error("Falha na etapa de compressão."); return False, None, original_size_mb, 0
            if step_successful and apply_ocr:
                logging.info("Iniciando Etapa de OCR...")
                ocr_output_path = os.path.join(temp_dir, "ocr_output.pdf")
                step_successful = self._apply_ocrmypdf(current_step_output, ocr_output_path, ocr_language)
                if step_successful: current_step_output = ocr_output_path; logging.info("OCR bem-sucedido.")
                else: logging.warning("Falha na etapa de OCR."); step_successful = True # Sucesso parcial
            if step_successful and os.path.exists(current_step_output):
                 with open(current_step_output, 'rb') as f: processed_bytes = f.read()
                 final_size_mb = len(processed_bytes) / 1024 / 1024; success = True
            else: logging.error("Falha no processamento ou arquivo final não encontrado.")
        return success, processed_bytes, original_size_mb, final_size_mb

    def image_to_pdf(self, image_files_bytes, output_pdf_path):
        try:
            valid_image_bytes = []
            for img_bytes in image_files_bytes:
                try:
                    img = Image.open(io.BytesIO(img_bytes)); img.verify()
                    img = Image.open(io.BytesIO(img_bytes))
                    if img.mode in ('P', 'RGBA', 'LA'):
                         try: img = img.convert('RGB')
                         except Exception as convert_err: logging.warning(f"Skip convert RGB: {convert_err}"); continue
                    byte_io = io.BytesIO(); save_format = 'JPEG' if img.format != 'PNG' else 'PNG'
                    img.save(byte_io, format=save_format); valid_image_bytes.append(byte_io.getvalue()); img.close()
                except Exception as img_err: logging.warning(f"Skip invalid image: {img_err}"); continue
            if not valid_image_bytes: logging.error("No valid images provided."); return False
            with open(output_pdf_path, "wb") as f: f.write(img2pdf.convert(valid_image_bytes))
            logging.info(f"Images converted to PDF: {output_pdf_path}"); return True
        except Exception as e: logging.error(f"Error image_to_pdf: {str(e)}"); return False

    def pdf_to_docx(self, input_pdf_path, output_docx_path, apply_ocr=False):
        pdf_to_process = input_pdf_path; ocr_applied_successfully = False
        try:
            with tempfile.TemporaryDirectory() as temp_docx_dir:
                 if apply_ocr:
                      if not self.ocrmypdf_installed: logging.warning("OCR requested but not installed.")
                      else:
                           logging.info("Applying OCR before DOCX conversion...")
                           temp_ocr_pdf_path = os.path.join(temp_docx_dir, "ocr_temp.pdf")
                           if self._apply_ocrmypdf(input_pdf_path, temp_ocr_pdf_path):
                                pdf_to_process = temp_ocr_pdf_path; ocr_applied_successfully = True; logging.info("OCR applied.")
                           else: logging.warning("OCR failed. Proceeding without it.")
                 logging.info(f"Converting {os.path.basename(pdf_to_process)} to DOCX.")
                 doc = fitz.open(pdf_to_process); document = Document(); has_content = False
                 for page_num in range(len(doc)):
                    page = doc.load_page(page_num); text = page.get_text("text")
                    if text.strip(): document.add_paragraph(text); has_content = True
                    image_list = page.get_images(full=True)
                    for img_index, img_info in enumerate(image_list):
                         xref = img_info[0]
                         try:
                              base_image = doc.extract_image(xref); image_bytes = base_image["image"]
                              image_ext = base_image["ext"]
                              temp_img_path = os.path.join(temp_docx_dir, f"p{page_num}_i{img_index}.{image_ext}")
                              with open(temp_img_path, "wb") as temp_img: temp_img.write(image_bytes)
                              try: document.add_picture(temp_img_path, width=Inches(6.0)); has_content = True
                              except Exception as pic_err: logging.warning(f"Cannot add picture p{page_num+1}_i{img_index}: {pic_err}")
                         except Exception as img_extract_err: logging.warning(f"Cannot extract image p{page_num+1}_i{img_index}: {img_extract_err}")
                    if page_num < len(doc) - 1: document.add_page_break()
                 doc.close()
                 if not has_content:
                      if apply_ocr and not ocr_applied_successfully: logging.warning("DOCX empty: No content found and OCR failed.")
                      else: logging.warning("DOCX maybe empty: No content extracted.")
                 document.save(output_docx_path); logging.info(f"PDF converted to DOCX: {output_docx_path}"); return True
        except Exception as e: logging.error(f"Error pdf_to_docx: {str(e)}"); return False

    def pdf_to_image(self, input_pdf_path, output_folder, image_format='png'):
        generated_images = []; doc = None
        try:
            if not os.path.exists(output_folder): os.makedirs(output_folder)
            doc = fitz.open(input_pdf_path)
            logging.info(f"Converting {len(doc)} PDF pages to {image_format.upper()}...")
            for page_num in range(len(doc)):
                 page = doc.load_page(page_num); zoom = 2.0; mat = fitz.Matrix(zoom, zoom)
                 pix = page.get_pixmap(matrix=mat, alpha=False)
                 output_image_path = os.path.join(output_folder, f"pagina_{page_num + 1}.{image_format}")
                 pix.save(output_image_path); generated_images.append(output_image_path)
            logging.info(f"{len(generated_images)} images generated in: {output_folder}"); return generated_images
        except Exception as e: logging.error(f"Error pdf_to_image: {str(e)}"); return None
        finally:
             if doc: doc.close() # Ensure the document is closed

    def create_zip_from_files(self, file_paths, output_zip_path):
        try:
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                 for file_path in file_paths: zipf.write(file_path, os.path.basename(file_path))
            logging.info(f"ZIP created: {output_zip_path}"); return True
        except Exception as e: logging.error(f"Error create_zip: {str(e)}"); return False

    def document_to_pdf(self, input_doc_path, output_pdf_path):
        if not self.libreoffice_path: logging.error("LibreOffice not found."); return False
        output_dir = os.path.dirname(output_pdf_path)
        input_basename = os.path.splitext(os.path.basename(input_doc_path))[0]
        expected_lo_output = os.path.join(output_dir, f"{input_basename}.pdf")
        if os.path.exists(expected_lo_output): os.unlink(expected_lo_output)
        if os.path.exists(output_pdf_path) and expected_lo_output != output_pdf_path: os.unlink(output_pdf_path)
        command = [self.libreoffice_path, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, input_doc_path]
        logging.info(f"Running conversion: {' '.join(command)}")
        try:
            process = subprocess.run(command, capture_output=True, check=False, text=True, timeout=120)
            if process.returncode != 0: logging.error(f"LO Error (code {process.returncode}): {process.stderr}"); return False
            if not os.path.exists(expected_lo_output): logging.error(f"Expected output '{expected_lo_output}' not found. Stderr: {process.stderr}"); return False
            if expected_lo_output != output_pdf_path: shutil.move(expected_lo_output, output_pdf_path); logging.info(f"Renamed to: {output_pdf_path}")
            if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0: logging.info(f"Doc converted to PDF: {output_pdf_path}"); return True
            else: logging.error(f"Final file '{output_pdf_path}' not found or empty."); return False
        except subprocess.TimeoutExpired: logging.error("LibreOffice conversion timed out."); return False
        except Exception as e: logging.error(f"Unexpected error converting document: {str(e)}"); return False
        finally:
             if os.path.exists(expected_lo_output) and expected_lo_output != output_pdf_path:
                  try: os.unlink(expected_lo_output)
                  except: pass

    # --- MÉTODO Juntar PDFs ---
    def merge_pdfs(self, pdf_byte_streams):
        """Junta múltiplos arquivos PDF (streams de bytes) em um único PDF."""
        if not pdf_byte_streams: return False, None, "Nenhum PDF fornecido."
        merged_writer = PdfWriter(); logging.info(f"Merging {len(pdf_byte_streams)} PDFs.")
        try:
            for idx, pdf_bytes in enumerate(pdf_byte_streams):
                try:
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    if not reader.pages: logging.warning(f"PDF {idx+1} empty/corrupt, skipping."); continue
                    for page in reader.pages: merged_writer.add_page(page)
                    logging.debug(f"Added PDF {idx+1} ({len(reader.pages)} pages).")
                except Exception as read_err: logging.error(f"Error reading PDF {idx+1}: {read_err}. Skipping."); # Continue
            if not merged_writer.pages: return False, None, "No valid content found to merge."
            output_stream = io.BytesIO(); merged_writer.write(output_stream); merged_writer.close()
            output_stream.seek(0); result_bytes = output_stream.getvalue()
            logging.info("PDF merge successful."); return True, result_bytes, "PDFs merged successfully."
        except Exception as e: error_msg = f"Unexpected error merging PDFs: {e}"; logging.exception(error_msg); return False, None, error_msg
        finally:
             if 'merged_writer' in locals() and hasattr(merged_writer, 'close'):
                  try: merged_writer.close()
                  except: pass
