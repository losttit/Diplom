import base64
import string

from plyer import notification

from Text2ImageAPI import Text2ImageAPI
from extractor import *
from summa.bart_sum import bart_sum, split_text
from summa.translator import translate_to_english
import random
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.title("Генератор конспектов")
        self.resizable(False, False)
        self.iconbitmap("resources/summary.ico")

        # Создаем Frame для выбора файлов
        file_frame = ctk.CTkFrame(self, fg_color=self.cget("bg"), bg_color=self.cget("bg"))
        file_frame.pack(pady=10)

        # Секция выбора файла
        self.file_path = ctk.CTkEntry(file_frame, width=240, placeholder_text="Выберите файл")
        self.file_path.pack(side="left", pady=10, padx=10)
        self.file_button = ctk.CTkButton(file_frame, width=100, text="Выбор", command=self.select_file)
        self.file_button.pack(side="left", pady=10)

        # Создаем Frame для нового заголовка
        title_frame = ctk.CTkFrame(self, fg_color=self.cget("bg"), bg_color=self.cget("bg"))
        title_frame.pack(pady=10)

        # Секция нового заголовка и генерации конспекта
        self.title_entry = ctk.CTkEntry(title_frame, width=240, placeholder_text="Новое название")
        self.title_entry.pack(side="left", pady=10, padx=10)

        # Создаем Frame для кнопки генерации
        gen_frame = ctk.CTkFrame(self, fg_color=self.cget("bg"), bg_color=self.cget("bg"))
        gen_frame.pack(pady=10)

        # Выпадающий список для расширения файла
        self.file_type = ctk.CTkComboBox(gen_frame, values=["pdf", "docx"])
        self.file_type.pack(side="left", pady=10, padx=10)
        self.generate_button = ctk.CTkButton(gen_frame, width=100, text="Генерировать", command=self.generate_summary)
        self.generate_button.pack(side="left", pady=10)

    @staticmethod
    def show(message):
        # Функция для вывода уведомлений
        notification.notify(title="Генератор конспектов", message=message, app_icon="resources/summary.ico", timeout=1)

    def select_file(self):
        file_path = ctk.filedialog.askopenfilename()
        self.file_path.delete(0, ctk.END)
        self.file_path.insert(0, file_path)

    def generate_summary(self):
        file_path = self.file_path.get()
        new_title = self.title_entry.get()
        file_type = self.file_type.get()

        if not file_path.endswith(('.pdf', '.docx')):
            CTkMessagebox(title="Ошибка", message="Выберите файл docx или pdf", icon="error")
            return

        try:
            if file_type == "pdf":
                self.show("Генерация конспекта для лекции с расширением PDF")

                print("Генерация конспекта для лекции с расширением PDF")
                sum_text, question_text = main(file_path, new_title)
                add_pdf(sum_text + "\n\n" + question_text, new_title)

                CTkMessagebox(title="Успех", message="Генерация конспекта прошла успешно!", icon="check")
            elif file_type == "docx":
                self.show("Генерация конспекта для лекции с расширением DOCX")
                print("Генерация конспекта для лекции с расширением DOCX")
                sum_text, question_text = main(file_path, new_title)
                add_docx(sum_text + "\n\n" + question_text, new_title)

                CTkMessagebox(title="Успех", message="Генерация конспекта прошла успешно!", icon="check")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            CTkMessagebox(title="Ошибка", message="Произошла ошибка", icon="error")


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
    # Количество вопросов равно количеству предложений в тексте, которые содержат более 5 слов
    sentences = sent_tokenize(summary)
    questions = []
    for sentence in sentences:
        words = [word for word in word_tokenize(sentence) if word.isalpha() and len(word) > 2]
        if len(words) > 5:
            random_word = random.choice(words)
            question = sentence.replace(random_word, "_____")
            questions.append((question, random_word))
    return questions


def main(file_path, new_title):
    try:
        docx_file_path = file_path
        lecture_text = extract_text(docx_file_path)
        sum_text = bart_sum(lecture_text)
        parts = split_text(sum_text, 300)
        translated_parts = [translate_to_english(part) for part in parts]
        main_phrases = [get_main_phrase(part) for part in translated_parts]
        print(main_phrases)

        # Генерация изображения
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/')
        model_id = api.get_model()
        uuid = api.generate(main_phrases, model_id)
        images = api.check_generation(uuid)
        for image in images:
            image_base64 = image
            image_data = base64.b64decode(image_base64)
            with open("output/lecture.jpg", "wb") as file:
                file.write(image_data)

        # Генерация вопросов
        questions = generate_questions(sum_text)
        all_words = [word for word in word_tokenize(sum_text) if word.isalpha()]
        question_text = ""
        for i, (question, answer) in enumerate(questions, start=1):
            question_text += f"{i}. {question}?\n"
            options = [answer] + random.sample([word for word in all_words if word != answer], 3)
            random.shuffle(options)
            for j, option in enumerate(options, start=1):
                question_text += f"{string.ascii_lowercase[j - 1]}. {option}\n"
            question_text += "\n"

        return sum_text, question_text
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        CTkMessagebox(title="Ошибка", message="Произошла ошибка", icon="error")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
