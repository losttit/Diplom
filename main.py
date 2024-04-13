from extractor import *
from summarization.easy_sum import easy_sum
from summarization.med_sum import med_sum
from summarization.hard_sum import hard_sum
from summarization.bart_sum import bart_sum

docx_file_path = 'resources/lecture1.docx'
lecture_text = extract_text(docx_file_path)
#Разделение на параграфы
# paragraphs = lecture_text.split("\n\n")
# for i, paragraph in enumerate(paragraphs):
#     processed_paragraph = bart_sum(paragraph)
#     add_text(processed_paragraph, f"xexe2_paragraph{i+1}")
#Мне лень сейчас доделывать. Все сумматоры подключены, разделение на параграфы работает.
#Нужно будет обозначить, типа указывайте одну тему, без названия темы, или как-то это обыграть.
#Каждый параграф должен быть до 1000 символов

sum_text = bart_sum(lecture_text)
add_text(sum_text, "xexe3")




