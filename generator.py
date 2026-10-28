# generator.py
import asyncio
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class Generator:
    def __init__(self, model_name="google/flan-t5-base", token=None, device=None):
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token="")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, token="")

        # Define device once
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    async def generate_answer(self, query, context, max_new_tokens=200):
        prompt = f"""
        Context:
        {context}

        Question: {query}

        Answer: list the department names clearly, one per line.
        """
        print("Prompt sent to generator:\n", prompt)

        def run_generation():
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


        # Run the blocking generation in a thread
        response = await asyncio.to_thread(run_generation)
        print("Raw answer from model:\n", response)
        return response


if __name__ == "__main__":
    gen = Generator(token="hf_xxx")
    context = "John Doe john.doe@example.com"
    answer = gen.generate_answer("What is John Doe's email?", context)
    print("Generated answer:", answer)
