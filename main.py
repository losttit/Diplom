import base64
import string
import random
import customtkinter as ctk
import re
from plyer import notification
from Text2ImageAPI import Text2ImageAPI
from extractor import *
from summa.bart_sum import bart_sum, split_text
from summa.translator import translate_to_english
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from CTkMessagebox import CTkMessagebox
from PIL import Image

# При первом запуске, убрать комментарии с 19-22 строки
# import nltk
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')

ctk.set_appearance_mode("light")  # dark, light
ctk.set_default_color_theme("blue")  # blue, dark-blue, green


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("460x240")
        self.title("Генератор конспектов")
        self.resizable(False, False)
        self.iconbitmap("resources/summary.ico")

        # Основной Frame
        main_frame = ctk.CTkFrame(self, width=410)  # fg_color="transparent"
        main_frame.pack(pady=(20, 10))

        # Поле "Выберите файл"
        self.file_path = ctk.CTkEntry(main_frame, width=270, placeholder_text="Выберите файл")
        self.file_path.grid(row=0, column=0, columnspan=2, sticky="w", pady=10, padx=(10, 0))

        # Кнопка "Выбор"
        self.file_button = ctk.CTkButton(main_frame, width=110, text="Выбор", command=self.select_file)
        self.file_button.grid(row=0, column=2, sticky="w", pady=10, padx=10)

        # Поле "Новое название"
        self.title_entry = ctk.CTkEntry(main_frame, width=390, placeholder_text="Новое название")
        self.title_entry.grid(row=1, column=0, columnspan=3, sticky="w", pady=10, padx=10)

        # "Выберите расширение файла"
        self.file_type_label = ctk.CTkLabel(main_frame, text="Выберите расширение файла", width=190)
        self.file_type_label.grid(row=2, column=0, sticky="w", pady=10, padx=(10, 0))

        # Выпадающий список выбора расширения файла (pdf/docx)
        self.file_type = ctk.CTkComboBox(main_frame, values=["pdf", "docx"], width=70)
        self.file_type.grid(row=2, column=1, sticky="w", pady=10, padx=(10, 0))

        # Кнопка "Генерировать"
        self.generate_button = ctk.CTkButton(main_frame, width=110, text="Генерировать", command=self.generate_summary)
        self.generate_button.grid(row=2, column=2, sticky="w", pady=10, padx=10)

        # Кнопка "Предпросмотр"
        preview_frame = ctk.CTkFrame(self, width=410, height=50)
        preview_frame.pack(pady=(0, 10))

        self.preview_button = ctk.CTkButton(preview_frame, width=390, text="Предпросмотр", command=self.preview_summary,
                                            state="disabled")
        self.preview_button.place(relx=0.5, rely=0.5, anchor="center")

    def preview_summary(self):
        # Окно предпросмотра
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Предпросмотр")
        preview_window.geometry("600x750")

        # Frame предпросмотра
        preview_frame = ctk.CTkFrame(preview_window)
        preview_frame.pack(pady=20, padx=20)

        # Загрузка изображения
        image = ctk.CTkImage(light_image=Image.open("output/lecture.jpg"), size=(200, 200))
        image_widget = ctk.CTkLabel(preview_frame, image=image, text="")
        image_widget.pack(pady=10, padx=10)

        # Текстовая коробка для конспекта и теста
        summary_text_box = ctk.CTkTextbox(preview_frame, width=580, height=380)
        summary_text_box.pack(pady=10, padx=10)

        # Внесение конспекта и теста в текстовую коробку
        summary_text_box.insert("1.0", self.sum_text + "\n\n" + self.question_text)

        # Кнопка "Закрыть"
        close_button = ctk.CTkButton(preview_window, text="Закрыть", command=preview_window.destroy)
        close_button.pack(pady=20, padx=20)

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
            CTkMessagebox(title="Ошибка", message="Выберите файл docx или pdf", icon="cancel")
            return

        try:
            if file_type == "pdf":
                self.show("Генерация конспекта для лекции с расширением PDF")
                print("Генерация конспекта для лекции с расширением PDF")
                self.sum_text, self.question_text = main(file_path)
                add_pdf(self.sum_text + "\n\n" + self.question_text, new_title)

                # Включение кнопки "Предпросмотр"
                self.preview_button.configure(state="normal")

                CTkMessagebox(title="Успех", message="Генерация конспекта прошла успешно!", icon="check")
            elif file_type == "docx":
                self.show("Генерация конспекта для лекции с расширением DOCX")
                print("Генерация конспекта для лекции с расширением DOCX")
                self.sum_text, self.question_text = main(file_path)
                add_docx(self.sum_text + "\n\n" + self.question_text, new_title)

                # Включение кнопки "Предпросмотр"
                self.preview_button.configure(state="normal")

                CTkMessagebox(title="Успех", message="Генерация конспекта прошла успешно!", icon="check")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            CTkMessagebox(title="Ошибка", message="Произошла ошибка", icon="cancel")


def get_main_phrase(text: str) -> str:
    # Извлечение ключевых фраз из текста
    lemmatizer = WordNetLemmatizer()
    text = ' '.join([lemmatizer.lemmatize(word) for word in word_tokenize(text)])
    vectorizer = TfidfVectorizer(max_features=2, stop_words=stopwords.words('english'))
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    return ' '.join(feature_names)


def generate_questions(summary: str) -> list:
    # Генерация вопросов из конспекта
    # Количество вопросов равно количеству предложений в тексте, которые содержат более 5 слов
    sentences = sent_tokenize(summary)
    questions = []
    for sentence in sentences:
        words = [word for word in word_tokenize(sentence) if word.isalpha() and len(word) > 2]
        if len(words) > 5:
            random_word = random.choice(words)
            word_pattern = r'\b' + re.escape(random_word) + r'\b'
            question = re.sub(word_pattern, '_____', sentence)
            questions.append((question, random_word))
    return questions


def main(file_path):
    try:
        lecture_text = extract_text(file_path)
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
            options = [answer.lower()] + random.sample(
                [word.lower() for word in all_words if word.lower() != answer.lower()], 3)
            random.shuffle(options)
            for j, option in enumerate(options, start=1):
                question_text += f"{string.ascii_lowercase[j - 1]}. {option}\n"
            question_text += "\n"

        return sum_text, question_text
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        CTkMessagebox(title="Ошибка", message="Произошла ошибка", icon="cancel")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
