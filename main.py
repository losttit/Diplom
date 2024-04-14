import string
from extractor import *
from summa.bart_sum import bart_sum
import random
from nltk.tokenize import sent_tokenize, word_tokenize
from diffusers import StableDiffusionPipeline
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

def get_main_phrase(text):
    # Лемматизация
    lemmatizer = WordNetLemmatizer()
    text = ' '.join([lemmatizer.lemmatize(word) for word in word_tokenize(text)])

    # Удаление стоп-слов
    vectorizer = TfidfVectorizer(max_features=2, stop_words=stopwords.words('english'))
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()

    return ' '.join(feature_names)


def generate_questions(summary):
    sentences = sent_tokenize(summary)
    questions = []
    for sentence in sentences:
        words = [word for word in word_tokenize(sentence) if word.isalpha()]  # только слова без знаков препинания
        if len(words) > 5:  # если предложение достаточно длинное
            random_word = random.choice(words)
            question = sentence.replace(random_word, "_____")
            questions.append((question, random_word))
    return questions


def main():
    docx_file_path = 'resources/lecture_ru.docx'
    lecture_text = extract_text(docx_file_path)
    sum_text = bart_sum(lecture_text)
    main_phrase = get_main_phrase(sum_text)
    print(main_phrase)
    # Генерация изображения
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
    pipe = pipe.to("cpu")
    image = pipe(main_phrase).images[0]
    image.save("resources/lecture.png")
    # Генерация теста
    questions = generate_questions(sum_text)
    all_words = [word for word in word_tokenize(sum_text) if
                 word.isalpha()]  # все слова из конспекта без знаков препинания
    for i, (question, answer) in enumerate(questions, start=1):
        print(f"{i}. {question}?")
        options = [answer] + random.sample([word for word in all_words if word != answer],
                                           3)  # генерируем три случайных варианта ответа
        random.shuffle(options)  # перемешиваем варианты ответа
        for j, option in enumerate(options, start=1):
            print(f"{string.ascii_lowercase[j - 1]}. {option}")
    add_text(sum_text, "xexe3")


if __name__ == "__main__":
    main()