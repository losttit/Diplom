import spacy

def easy_sum(lecture_text):
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe("textrank")

    doc = nlp(lecture_text)

    for sent in doc._.textrank.summary(): # for sent in doc._.textrank.summary(limit_phrases=10, limit_sentences=2):
          print(sent)