import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
from Modules.rag_3.rag_retriever import init_rag, retrieve_context
from Modules.rag_3.prompt_builder import build_user_prompt

# API Setting
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:4b"

app = FastAPI(title="HKBU Study Companion")

# Query Format
class Query(BaseModel):
    question: str
    context: list = []
    is_search: bool = False
    use_neural_retrieval: bool = False

def complete_document(message: str):
    payload = {
        "model": MODEL,
        "messages": [message],
        "stream": True,
        "options": {
            "num_predict": 2048,
            "temperature": 0.3
        }
    }
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
            r.raise_for_status()
            for chunk in r.iter_lines():
                if chunk:
                    data = json.loads(chunk)
                    token = data.get("message", {}).get("content", "")
                    yield token

    except requests.exceptions.ConnectionError:
        yield "\nerror: Can't find ollama serve"
    except Exception as e:
        yield f"\nerror: {str(e)}"

# API
@app.post("/ask")
def ask(q: Query):

    context, results, stats = retrieve_context(q.question, top_k=3)
    user_prompt = build_user_prompt(
        user_query=q.question,
        retrieved_context=context,
        search_mode=q.is_search,
        think_mode=False
    )
    prompt = q.context + user_prompt
    return StreamingResponse(
        complete_document(prompt),
        media_type="text/plain; charset=utf-8"
    )
    
init_rag()

print("✅ Backend Address: http://localhost:8326")
print("✅ Backend Document: http://localhost:8326/docs")