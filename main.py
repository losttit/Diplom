import string
from extractor import *
from summa.bart_sum import bart_sum, split_text
from summa.translator import translate_to_english
import random
from nltk.tokenize import sent_tokenize, word_tokenize
from diffusers import StableDiffusionPipeline
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def get_main_phrase(text: str) -> str:
    """Извлекаем ключевые фразы из текста"""
    lemmatizer = WordNetLemmatizer()
    text = ' '.join([lemmatizer.lemmatize(word) for word in word_tokenize(text)])
    vectorizer = TfidfVectorizer(max_features=2, stop_words=stopwords.words('english'))
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    return ' '.join(feature_names)


def generate_questions(summary: str) -> list:
    """Генерация вопросов из конспекта"""
    sentences = sent_tokenize(summary)
    questions = []
    for sentence in sentences:
        words = [word for word in word_tokenize(sentence) if word.isalpha()]
        if len(words) > 5:
            random_word = random.choice(words)
            question = sentence.replace(random_word, "_____")
            questions.append((question, random_word))
    return questions


def main():
    docx_file_path = 'resources/lecture_ru.docx'
    try:
        lecture_text = extract_text(docx_file_path)
        sum_text = bart_sum(lecture_text)
        parts = split_text(sum_text, 300)
        translated_parts = [translate_to_english(part) for part in parts]
        main_phrases = [get_main_phrase(part) for part in translated_parts]
        print(main_phrases)

        # Генерация изображения
        # model_id = "runwayml/stable-diffusion-v1-5"
        # pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
        # pipe = pipe.to("cpu")
        # image = pipe(main_phrases).images[0]
        # image.save("resources/lecture.png")

        # Генерация вопросов
        questions = generate_questions(sum_text)
        all_words = [word for word in word_tokenize(sum_text) if word.isalpha()]
        for i, (question, answer) in enumerate(questions, start=1):
            print(f"{i}. {question}?")
            options = [answer] + random.sample([word for word in all_words if word != answer], 3)
            random.shuffle(options)
            for j, option in enumerate(options, start=1):
                print(f"{string.ascii_lowercase[j - 1]}. {option}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()