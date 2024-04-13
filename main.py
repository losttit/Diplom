from extractor import *
from summarization.easy_sum import easy_sum
from summarization.med_sum import med_sum
from summarization.hard_sum import hard_sum
from summarization.bart_sum import bart_sum

docx_file_path = 'resources/lecture1.pdf'
lecture_text = extract_text(docx_file_path)
sum_text = bart_sum(lecture_text)
add_text(sum_text, "xexe3")




