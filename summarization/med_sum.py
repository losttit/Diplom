from transformers import pipeline

def med_sum(lecture_text):
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    summary = summarizer(lecture_text, max_length=1000, min_length=30, do_sample=False)
    return summary[0]['summary_text']