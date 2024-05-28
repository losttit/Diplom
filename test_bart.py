from transformers import pipeline
from summa.translator import translate_to_english, translate_to_russian
from summa.bart_sum import split_text
import sacrebleu
import nltk
from nltk.translate.meteor_score import meteor_score

# При первом запуске, убрать комментарии с 9-10 строки
# nltk.download('wordnet')
# nltk.download('punkt')


def bart_sum(lecture_text):
    # Загрузка модели суммаризации
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    # Разделение текста лекции на части длиной до 300 слов
    parts = split_text(lecture_text, 300)
    summaries = []

    for i, part in enumerate(parts):
        # Перевод части текста на английский язык
        part_in_english = translate_to_english(part)
        word_count_en = len(part_in_english.split())
        min_length = word_count_en // 3
        # Генерация суммаризации части текста
        summary = summarizer(part_in_english, do_sample=False, min_length=min_length, max_length=min_length + 50)
        # Перевод суммаризации обратно на русский язык
        summary_in_russian = translate_to_russian(summary[0]['summary_text'])
        # Удаление лишних символов
        summary_in_russian = summary_in_russian.replace('&quot;', '"')
        summaries.append(summary_in_russian)

    # Объединение всех частей в один конспект
    final_summary = ' '.join(summaries).strip()
    print(f"Сгенерированный конспект: {final_summary}")
    return final_summary


def evaluate_summaries(generated_summary, reference_summary):
    if generated_summary is None or reference_summary is None:
        raise ValueError("Сгенерированный или эталонный конспект равен None")

    # Очистка текста
    generated_summary = generated_summary.strip()
    reference_summary = reference_summary.strip()

    print(f"Эталонный конспект: {reference_summary}")

    # Оценка BLEU с использованием библиотеки sacrebleu
    bleu_score = sacrebleu.corpus_bleu([generated_summary], [[reference_summary]]).score

    # Токенизация конспектов для оценки METEOR
    reference_tokens = nltk.word_tokenize(reference_summary)
    generated_tokens = nltk.word_tokenize(generated_summary)

    # Оценка METEOR с использованием библиотеки nltk
    meteor = meteor_score([reference_tokens], generated_tokens)

    return bleu_score, meteor


# Пример использования
# Текст лекции для генерации конспекта
lecture_text = '''Экономическая теория изучает законы экономического развития. Термин "экономика" и его производное "эконом" происходят от слияния греческих слов "ойкос" - дом, домохозяйство и "номос" - правление, закон. Итак, экономика - это управление хозяйством, правила ведения сельского хозяйства.
В области экономической науки существуют проблемы, которые волнуют всех без исключения: когда и какие виды работ следует выполнять, как их оплачивать, сколько товаров можно купить на определенную денежную единицу и т.д.
В экономической теории жизненные проблемы изучаются не с индивидуальной, а с социальной точки зрения.
Любое общество сталкивается с тремя основными и взаимосвязанными проблемами экономики: что должно производиться? Как производятся эти продукты? и для кого этот продукт предназначен?
Экономические ресурсы - это природные, человеческие и производственные ресурсы, которые используются для производства товаров и услуг. К ним относятся промышленные и сельскохозяйственные предприятия. здания, оборудование, инструменты, станки, различные виды рабочей силы, земля и все виды полезных ископаемых. Все экономические ресурсы состоят из материальных и человеческих ресурсов. Кроме того, существуют факторы производства: земля, капитал, рабочая сила, предпринимательские способности. Это свойство всех экономик. ресурсы ограничены.
Экономическая теория - это наука об отношениях между людьми, связанных с производством, обменом, распределением и потреблением материальных благ и услуг, а также о способах эффективного использования ограниченных производственных ресурсов.
Экономическая теория выполняет две основные функции - практическую и познавательную.
Когнитивная функция заключается в установлении взаимосвязей между фактами, их обобщении и выводе определенных закономерностей. Существует математический аппарат для изучения экономических явлений и механизм построения экономических моделей. Экономическая теория делится на два основных направления - макро- и микроэкономику. Макроэкономический анализ изучает экономику в целом или ее основные компоненты. Он оперирует такими величинами, как валовой выпуск, валовой доход, общий уровень цен и т.д.
Микроэкономический анализ изучает конкретные экономические единицы: отрасль, компанию или отдельные показатели этих единиц. Он оперирует такими понятиями, как спрос, предложение и издержки производства.'''

# Эталонный конспект
reference_summary = '''Экономические ресурсы - это природные, людские и производственные ресурсы, которые используются для производства товаров; экономические ресурсы состоят из материальных и людских ресурсов; есть также факторы производства: земля, капитал и труд, для которых экономические ресурсы ограничены; экономическая теория рассматривает проблемы жизни с социальной точки зрения.'''

# Генерация конспекта
generated_summary = bart_sum(lecture_text)

# Оценка конспекта
if generated_summary and reference_summary:
    bleu_score, meteor = evaluate_summaries(generated_summary, reference_summary)
    print("Значение метрики BLEU:", bleu_score)
    print("Значение метрики METEOR:", meteor)
else:
    print("Ошибка: Пустой сгенерированный или эталонный текст")
