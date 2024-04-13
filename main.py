from extractor import *
from summarization.easy_sum import easy_sum
from summarization.med_sum import med_sum
from summarization.hard_sum import hard_sum
from summarization.bart_sum import bart_sum

def main():
    docx_file_path = 'resources/lecture_ru.docx'
    lecture_text = extract_text(docx_file_path)
    sum_text = bart_sum(lecture_text)
    add_text(sum_text, "xexe3")

if __name__ == "__main__":
    main()