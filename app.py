from fastapi import FastAPI, Request
from pydantic import BaseModel
from db_connector import get_texts
from retriever import Retriever
from generator import Generator
from botbuilder.core import BotFrameworkAdapter, TurnContext, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# --- Load records from SQL DB ---
records = get_texts()

# Load embedding model
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", token="")

# Generate embeddings for each record's text
texts = [r["text"] for r in records]
embeddings = embedder.encode(texts, convert_to_numpy=True).astype("float32")

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

print("Number of records loaded:", len(records))
print("Index dimension:", index.d)
print("First record sample:", records[0])

retriever = Retriever(records=records, index=index)
generator = Generator()

# --- Adapter setup for Emulator (no credentials needed locally) ---
settings = BotFrameworkAdapterSettings("", "")
adapter = BotFrameworkAdapter(settings)

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Question):
    # Step 1: Retrieve relevant context
    relevant_records = retriever.get_relevant(q.question, k=7)
    if not relevant_records:
        return {"answer": "not available", "context_used": []}

    # Deduplicate by text (or id if guaranteed unique)
    unique_texts = []
    seen = set()
    for r in relevant_records:
        if r["text"] not in seen:
            seen.add(r["text"])
            unique_texts.append(r["text"])

    context = " ".join(unique_texts)

    # Step 2: Generate answer
    if not context.strip():
        return {"answer": "not available", "context_used": relevant_records}
    else:
        answer = await generator.generate_answer(q.question, context)
        return {"answer": answer, "context_used": relevant_records}


@app.post("/api/messages")
async def messages(req: Request):
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    async def logic(turn_context: TurnContext):
        logging.info(f"Received activity type: {turn_context.activity.type}")

        if turn_context.activity.type == "message":
            user_query = turn_context.activity.text
            relevant_records = retriever.get_relevant(user_query, k=3)
            context = "\n".join([r["text"] for r in relevant_records])
            # Call sync generator (no await)
            answer = await generator.generate_answer(user_query, context)
            await turn_context.send_activity(answer)


        elif turn_context.activity.type == "conversationUpdate":
            members_added = turn_context.activity.members_added
            if members_added:
                for member in members_added:
                    if member.id != turn_context.activity.recipient.id:
                        await turn_context.send_activity("Hello and welcome! Ask me about HumanResources.")

        else:
            await turn_context.send_activity(f"Unhandled activity type: {turn_context.activity.type}") 
            



    try:
        await adapter.process_activity(activity, auth_header, logic)
    except Exception as e:
        logging.exception(f"Error processing activity: {e}")
        raise
    return {}
