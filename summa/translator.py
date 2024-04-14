from transformers import MarianMTModel, MarianTokenizer

# ru-en
model_name = 'Helsinki-NLP/opus-mt-ru-en'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)
# en-ru
model_name_ru = 'Helsinki-NLP/opus-mt-en-ru'
tokenizer_ru = MarianTokenizer.from_pretrained(model_name_ru)
model_ru = MarianMTModel.from_pretrained(model_name_ru)


def translate_to_english(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    translated = model.generate(**inputs)
    return [tokenizer.decode(t, skip_special_tokens=True) for t in translated][0]


def translate_to_russian(text):
    inputs = tokenizer_ru(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    translated = model_ru.generate(**inputs)
    return [tokenizer_ru.decode(t, skip_special_tokens=True) for t in translated][0]