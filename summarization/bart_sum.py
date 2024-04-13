from transformers import pipeline

def split_text(text, word_limit): # Разделение лекции на части по 300 для лучшей генерации конспектов
    words = text.split()
    parts = []
    temp_part = []
    word_count = 0

    for word in words:
        if word_count + len(word.split()) <= word_limit:
            temp_part.append(word)
            word_count += len(word.split())
        else:
            parts.append(' '.join(temp_part))
            temp_part = [word]
            word_count = len(word.split())
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

# def bart_sum(lecture_text):
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
#     summary = summarizer(lecture_text, do_sample=False, min_length=100, max_length=400)
#     return summary[0]['summary_text']