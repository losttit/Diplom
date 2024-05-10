import os
import docx2txt
from CTkMessagebox import CTkMessagebox
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF

# Извлечение данных из файлов формата PDF/docx
def extract_text(filename):
    if filename.endswith('.pdf'):
        pdf_reader = PdfReader(filename)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif filename.endswith('.docx'):
        return docx2txt.process(filename)
    else:
        CTkMessagebox(title="Ошибка", message="Выберите файл docx или pdf", icon="error")
        print("Ошибка: Выберите файл docx или pdf")
        return ''


def add_docx(text, doc_name):
    if os.path.exists(doc_name):
        os.remove(doc_name)
    if not doc_name.endswith('.docx'):
        doc_name += '.docx'
    doc = Document()
    doc.add_paragraph(text)
    doc.save("resources/" + doc_name)


def add_pdf(text, pdf_name):
    if os.path.exists(pdf_name):
        os.remove(pdf_name)
    if not pdf_name.endswith('.pdf'):
        pdf_name += '.pdf'
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVuSans", "", "resources/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVuSans", "", 12)
    pdf.multi_cell(0, 10, txt=text, align='L')
    pdf.output("resources/" + pdf_name)
