import base64
import string
import random
import customtkinter as ctk
import re
import os
from plyer import notification  # Для системных уведомлений
from Text2ImageAPI import Text2ImageAPI  # Кастомный API для генерации изображений
from extractor import *  # Функции для извлечения текста из файлов
from summa.bart_sum import bart_sum, split_text  # Модели суммаризации текста
from summa.translator import translate_to_english  # Функции перевода текста
from nltk.tokenize import sent_tokenize, word_tokenize  # Токенизация текста
from sklearn.feature_extraction.text import TfidfVectorizer  # TF-IDF векторизация
from nltk.corpus import stopwords  # Стоп-слова
from nltk.stem import WordNetLemmatizer  # Лемматизация слов
from CTkMessagebox import CTkMessagebox  # Пользовательские окна сообщений
from PIL import Image  # Библиотека для обработки изображений
import concurrent.futures  # Параллельное выполнение задач

import nltk
# Проверка установлен ли nltk
nltk.corpus.wordnet.ensure_loaded()
# При первом запуске, убрать комментарии с 24-26 строки
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')

ctk.set_appearance_mode("light")  # Режим отображения: dark, light
ctk.set_default_color_theme("blue")  # Тема приложения: blue, dark-blue, green


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("460x240")  # Размер окна приложения
        self.title("Генератор конспектов")  # Заголовок окна
        self.resizable(False, False)  # Отключение изменения размера окна
        self.iconbitmap("resources/summary.ico")  # Иконка приложения

        self.setup_ui()  # Инициализация пользовательского интерфейса

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, width=410)  # Основная рамка
        main_frame.pack(pady=(20, 10))

        self.file_path = ctk.CTkEntry(main_frame, width=270,
                                      placeholder_text="Выберите файл")  # Поле для ввода пути к файлу
        self.file_path.grid(row=0, column=0, columnspan=2, sticky="w", pady=10, padx=(10, 0))

        self.file_button = ctk.CTkButton(main_frame, width=110, text="Выбор",
                                         command=self.select_file)  # Кнопка выбора файла
        self.file_button.grid(row=0, column=2, sticky="w", pady=10, padx=10)

        self.title_entry = ctk.CTkEntry(main_frame, width=390,
                                        placeholder_text="Новое название")  # Поле для ввода нового названия
        self.title_entry.grid(row=1, column=0, columnspan=3, sticky="w", pady=10, padx=10)

        self.file_type_label = ctk.CTkLabel(main_frame, text="Выберите расширение файла",
                                            width=190)  # Надпись для выбора расширения файла
        self.file_type_label.grid(row=2, column=0, sticky="w", pady=10, padx=(10, 0))

        self.file_type = ctk.CTkComboBox(main_frame, values=["pdf", "docx"],
                                         width=70)  # Выпадающий список для выбора расширения файла
        self.file_type.grid(row=2, column=1, sticky="w", pady=10, padx=(10, 0))

        self.generate_button = ctk.CTkButton(main_frame, width=110, text="Генерировать",
                                             command=self.generate_summary)  # Кнопка генерации конспекта
        self.generate_button.grid(row=2, column=2, sticky="w", pady=10, padx=10)

        preview_frame = ctk.CTkFrame(self, width=410, height=50)  # Рамка для кнопки предпросмотра
        preview_frame.pack(pady=(0, 10))

        self.preview_button = ctk.CTkButton(preview_frame, width=390, text="Предпросмотр", command=self.preview_summary,
                                            state="disabled")  # Кнопка предпросмотра
        self.preview_button.place(relx=0.5, rely=0.5, anchor="center")

    def preview_summary(self):
        preview_window = ctk.CTkToplevel(self)  # Создание окна предпросмотра
        preview_window.title("Предпросмотр")
        preview_window.geometry("600x750")

        preview_frame = ctk.CTkFrame(preview_window)  # Рамка для содержимого окна предпросмотра
        preview_frame.pack(pady=20, padx=20)

        try:
            image_path = "output/lecture.jpg"
            if os.path.exists(image_path):
                image = ctk.CTkImage(light_image=Image.open(image_path), size=(200, 200))
                image_widget = ctk.CTkLabel(preview_frame, image=image, text="")
                image_widget.pack(pady=10, padx=10)
        except FileNotFoundError:
            pass

        summary_text_box = ctk.CTkTextbox(preview_frame, width=580,
                                          height=380)  # Текстовое поле для конспекта и вопросов
        summary_text_box.pack(pady=10, padx=10)
        summary_text_box.insert("1.0", self.sum_text + "\n\n" + self.question_text)

        close_button = ctk.CTkButton(preview_window, text="Закрыть",
                                     command=preview_window.destroy)  # Кнопка закрытия окна предпросмотра
        close_button.pack(pady=20, padx=20)

    @staticmethod
    def show(message):
        # Функция для вывода уведомлений
        notification.notify(title="Генератор конспектов", message=message, app_icon="resources/summary.ico",
                            timeout=1)  # Системное уведомление

    def select_file(self):
        file_path = ctk.filedialog.askopenfilename()  # Диалог выбора файла
        self.file_path.delete(0, ctk.END)
        self.file_path.insert(0, file_path)

    def generate_summary(self):
        file_path = self.file_path.get()  # Получение пути к файлу
        new_title = self.title_entry.get()  # Получение нового названия файла
        file_type = self.file_type.get()  # Получение выбранного расширения файла

        if not file_path.endswith(('.pdf', '.docx')):
            CTkMessagebox(title="Ошибка", message="Выберите файл docx или pdf",
                          icon="cancel")  # Проверка расширения файла
            return

        try:
            self.show(f"Генерация конспекта для лекции с расширением {file_type.upper()}")
            print(f"Генерация конспекта для лекции с расширением {file_type.upper()}")

            self.sum_text, self.question_text, image_exists = main(file_path)

            if file_type == "pdf":
                add_pdf(self.sum_text + "\n\n" + self.question_text, new_title,
                        image_exists=image_exists)  # Генерация PDF
            else:
                add_docx(self.sum_text + "\n\n" + self.question_text, new_title,
                         image_exists=image_exists)  # Генерация DOCX

            self.preview_button.configure(state="normal")
            CTkMessagebox(title="Успех", message="Генерация конспекта прошла успешно!",
                          icon="check")  # Сообщение об успешной генерации

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            CTkMessagebox(title="Ошибка", message="Произошла ошибка", icon="cancel")  # Сообщение об ошибке


def get_main_phrase(text: str) -> str:
    try:
        # Инициализация необходимых компонентов
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        # Токенизация текста
        words = word_tokenize(text.lower())
        # Лемматизация и удаление стоп-слов
        lemmatized_words = [lemmatizer.lemmatize(word) for word in words if word.isalnum() and word not in stop_words]
        # Объединение лемматизированных слов обратно в строку
        processed_text = ' '.join(lemmatized_words)
        # Векторизация текста
        vectorizer = TfidfVectorizer(max_features=2)
        tfidf_matrix = vectorizer.fit_transform([processed_text])
        # Получение ключевых фраз
        feature_names = vectorizer.get_feature_names_out()
        return ' '.join(feature_names)
    except Exception as e:
        print(f"Ошибка в get_main_phrase: {e}")
        return ""


def generate_questions(summary: str) -> list:
    try:
        # Генерация вопросов из конспекта
        sentences = sent_tokenize(summary)  # Разделение текста на предложения
        questions = []
        for sentence in sentences:
            words = [word for word in word_tokenize(sentence) if
                     word.isalpha() and len(word) > 2]  # Токенизация и фильтрация слов
            if len(words) > 5:
                random_word = random.choice(words)  # Выбор случайного слова
                word_pattern = r'\b' + re.escape(random_word) + r'\b'
                question = re.sub(word_pattern, '_____', sentence)  # Замена слова на пустое место
                questions.append((question, random_word))
        return questions
    except Exception as e:
        print(f"Ошибка в generate_questions: {e}")
        return []


def main(file_path):
    try:
        # Проверка и удаление старого изображения
        image_path = "output/lecture.jpg"
        if os.path.exists(image_path):
            os.remove(image_path)

        lecture_text = extract_text(file_path)  # Извлечение текста из файла
        sum_text = bart_sum(lecture_text)  # Суммаризация текста
        parts = split_text(sum_text, 300)  # Разделение текста на части

        with concurrent.futures.ThreadPoolExecutor() as executor:
            translated_parts = list(executor.map(translate_to_english, parts))  # Параллельный перевод частей текста
            main_phrases = list(executor.map(get_main_phrase, translated_parts))  # Параллельное извлечение ключевых фраз

        image_exists = False
        try:
            api = Text2ImageAPI('https://api-key.fusionbrain.ai/')  # Инициализация API для генерации изображений
            model_id = api.get_model()
            print(f"Основные фразы: {main_phrases}")
            uuid = api.generate(main_phrases, model_id)
            images = api.check_generation(uuid)

            if images:
                # Сохранение нового изображения
                for image in images:
                    image_base64 = image
                    image_data = base64.b64decode(image_base64)
                    with open(image_path, "wb") as file:
                        file.write(image_data)
                image_exists = True
            else:
                raise Exception(" API в данный момент недоступно")
        except Exception as e:
            print(f"Ошибка при генерации изображения: {e}.")
            CTkMessagebox(title="Внимание", message="Сейчас API недоступно, генерация изображения невозможна",
                          icon="warning")

        questions = generate_questions(sum_text)  # Генерация вопросов по конспекту
        all_words = [word for word in word_tokenize(sum_text) if word.isalpha()]
        question_text = ""
        for i, (question, answer) in enumerate(questions, start=1):
            question_text += f"{i}. {question}?\n"
            options = [answer.lower()] + random.sample(
                [word.lower() for word in all_words if word.lower() != answer.lower()], 3)
            random.shuffle(options)  # Перемешивание вариантов ответов
            for j, option in enumerate(options, start=1):
                question_text += f"{string.ascii_lowercase[j - 1]}. {option}\n"
            question_text += "\n"

        return sum_text, question_text, image_exists
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        CTkMessagebox(title="Ошибка", message="Произошла ошибка", icon="cancel")  # Сообщение об ошибке
        return None, None, None  # Возвращение значений None во избежание ошибки распаковки



if __name__ == "__main__":
    app = Application()  # Запуск приложения
    app.mainloop()
