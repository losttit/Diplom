from transformers import PegasusForConditionalGeneration
from transformers import PegasusTokenizer

def hard_sum(lecture_text):
    model_name = "google/pegasus-xsum"

    pegasus_tokenizer = PegasusTokenizer.from_pretrained(model_name)

    pegasus_model = PegasusForConditionalGeneration.from_pretrained(model_name)

    tokens = pegasus_tokenizer(lecture_text, truncation=True, padding="longest", return_tensors="pt")

    encoded_summary = pegasus_model.generate(**tokens)

    decoded_summary = pegasus_tokenizer.decode(
        encoded_summary[0],
        skip_special_tokens=True
    )
    print(decoded_summary)