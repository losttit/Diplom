﻿# Дипломный проект 
### "Разработка генератора тестов и краткого конспекта лекции с использованием нейросети"

Генератор конспектов - это приложение, которое помогает создавать конспекты лекций из файлов в формате PDF или DOCX. Оно использует технологии искусственного интеллекта для извлечения ключевых фраз, генерации тестов и создания изображений.


## Функциональность

- Выбор файла в формате PDF или DOCX
- Генерация конспекта с помощью алгоритма BART
- Извлечение ключевых фраз с помощью TF-IDF
- Генерация вопросов на основе конспекта
- Создание изображений с помощью Text2ImageAPI
- Вывод уведомлений в консоль о ходе генерации конспекта

## Использование

1. Перед первым использованием установите requirments.txt:
   ``` pip install -r requirements.txt ```
2. Запустите приложение и выберите файл в формате PDF или DOCX (для удобства используйте папку input для своих конспектов).
3. Введите новое название для конспекта.
4. Выберите тип файла (PDF или DOCX).
5. Нажмите кнопку "Генерировать".
6. Приложение будет генерировать конспект, извлекать ключевые фразы, генерировать вопросы и создавать изображения.
7. После завершения генерации конспекта будет сохранен в формате PDF или DOCX в папку output.

## Требования 
- Python 3.12

## Автор
Пегасин Андрей
