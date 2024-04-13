from transformers import pipeline

# Разделение лекции на части по 300 слов(берутся полные предложения до точки) для лучшей генерации конспектов
def split_text(text, word_limit):
    words = text.split()
    parts = []
    temp_part = []
    word_count = 0
    for word in words:
        temp_part.append(word)
        word_count += len(word.split())
        if word_count >= word_limit and word.endswith('.'):
            parts.append(' '.join(temp_part))
            temp_part = []
            word_count = 0

    if temp_part:
        parts.append(' '.join(temp_part))
    return parts

def bart_sum(lecture_text): # Обученная модель машинного обучения, готовая
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    parts = split_text(lecture_text, 300)
    summaries = []

    for i, part in enumerate(parts):
        word_count = len(part.split())
        min_length = word_count // 3
        print(f"Часть {i+1}. Количество слов: {word_count}")
        summary = summarizer(part, do_sample=False, min_length=min_length, max_length=min_length+50)
        summaries.append(summary[0]['summary_text'])

    return ' '.join(summaries)