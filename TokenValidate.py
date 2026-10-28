from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name, token="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")
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, token="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")

inputs = tokenizer("Hello world", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))