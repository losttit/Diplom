import os
import docx2txt
from docx import Document

def extract_text(filename):
    return docx2txt.process(filename)

def add_text(text, doc_name):
    if os.path.exists(doc_name):
        os.remove(doc_name)
    if not doc_name.endswith('.docx'):
        doc_name += '.docx'
    doc = Document()
    doc.add_paragraph(text)
    doc.save("resources/" + doc_name)