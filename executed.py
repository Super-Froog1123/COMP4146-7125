import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
from Modules.conversion_1.conversion import messages_to_prompt
from Modules.conversion_1.prompt_factor import PromptBuilder

# API Setting
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

app = FastAPI(title="HKBU Study Companion")
builder = PromptBuilder()

class Query(BaseModel):
    """HKBU Study Assistant providing three mutually exclusive working modes.
    
    ====================   ===========   ===============   =====================
    Mode                    is_search     is_study_plan     Optional Features
    ====================   ===========   ===============   =====================
    Normal Mode             False         False             think_mode
    Search Mode (RAG)       True          False             use_embedding_retrieval
    Study Plan Mode         False         True              -
    ====================   ===========   ===============   =====================
    
    Constraints:
        - is_search and is_study_plan cannot both be True
        - use_embedding_retrieval only takes effect when is_search=True
        - think_mode only takes effect when is_search=False and is_study_plan=False
    """

    question: str                           # user query
    context: list = []                      # history record
    system_prompt: str = ""                 # system role setting
    is_search: bool = False                 # enable search mode?
    use_embedding_retrieval: bool = False   # using embedding retrieval?(if not, use lexical retrieval)
    think_mode: bool = False                # enable think mode?
    is_study_plan: bool = False             # ebable study plan mode?

def complete_document(prompt: str):
    """Generate streaming response from Ollama"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "num_predict": 2048,
            "temperature": 0.3
        }
    }
    
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    
                    if data.get("done", False):
                        break
                        
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {line}")
                    continue
                    
    except requests.exceptions.ConnectionError:
        yield "\nError: Cannot connect to Ollama server. Please ensure Ollama is running."
    except requests.exceptions.Timeout:
        yield "\nError: Request timeout after 120 seconds."
    except Exception as e:
        yield f"\nError: {str(e)}"

# API
@app.post("/ask")
def ask(q: Query):

    full_prompt_list = builder.get_full_prompt_list(
        question=q.question,
        context = q.context,
        system_prompt = q.system_prompt,
        is_search = q.is_search,
        use_embedding_retrieval= q.use_embedding_retrieval,
        think_mode = q.think_mode,
        is_study_plan = q.is_study_plan
    )

    full_prompt = messages_to_prompt(full_prompt_list)
    return StreamingResponse(
        complete_document(full_prompt),
        media_type="text/plain; charset=utf-8"
    )
    

print("✅ Backend Address: http://localhost:8326")
print("✅ Backend Document: http://localhost:8326/docs")