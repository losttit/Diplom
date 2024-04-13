import os
import docx2txt
from PyPDF2 import PdfReader
from docx import Document

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
        print("Ошибка: Выберите файл docx или pdf")
        return ''


def add_text(text, doc_name):
    if os.path.exists(doc_name):
        os.remove(doc_name)
    if not doc_name.endswith('.docx'):
        doc_name += '.docx'
    doc = Document()
    doc.add_paragraph(text)
    doc.save("resources/" + doc_name)