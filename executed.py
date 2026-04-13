import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json

# API Setting
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

app = FastAPI(title="HKBU Study Companion")

# Query Format
class Query(BaseModel):
    question: str
    context: str = "None"
    is_search: bool = False
    use_neural_retrieval: bool = False

def build_prompt(context: str, question: str):
    return f"""
You are a helpful HKBU study assistant.
Answer the question based ONLY on the provided context.
If you don't know, say "I don't have enough information."

Context:
{context}

Question:
{question}

Answer (concise with citation):
"""

def complete_document(prefix: str):
    payload = {
        "model": MODEL,
        "prompt": prefix,
        "stream": True,
        "raw": True,
        "options": {
            "num_predict": 256,
            "temperature": 0.3
        }
    }
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
            r.raise_for_status()
            for chunk in r.iter_lines():
                if chunk:
                    data = json.loads(chunk)
                    token = data.get("response", "")
                    yield token

    except requests.exceptions.ConnectionError:
        yield "\n❌ error: Can't find ollama serve"
    except Exception as e:
        yield f"\n❌ error: {str(e)}"

# API
@app.post("/ask")
def ask(q: Query):
    prompt = build_prompt(q.context, q.question)
    return StreamingResponse(
        complete_document(prompt),
        media_type="text/plain; charset=utf-8"
    )
    

print("✅ Backend Address: http://localhost:8326")
print("✅ Backend Document: http://localhost:8326/docs")