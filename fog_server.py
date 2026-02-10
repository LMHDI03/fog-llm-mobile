import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from rag import PatientRAG  # ton rag.py
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "phi3:latest")  # aligne avec ollama list

rag = None

class PromptRequest(BaseModel):
    prompt: str

@app.on_event("startup")
def startup():
    global rag
    try:
        rag = PatientRAG()
        print("[FOG] RAG index loaded ✅")
    except Exception as e:
        rag = None
        print(f"[FOG] RAG failed ❌ -> {e}")

@app.get("/health")
def health():
    return {"status": "ok", "rag": rag is not None}

@app.post("/generate")
def generate(req: PromptRequest):
    # 1) context RAG (si dispo)
    context = rag.search(req.prompt, k=2) if rag else "RAG indisponible."

    full_prompt = f"""Tu es un assistant médical professionnel.
Utilise UNIQUEMENT la fiche patient ci-dessous pour répondre.
Si l'information n'est pas présente, dis clairement "Information non disponible dans la fiche".

FICHE PATIENT:
{context}

QUESTION:
{req.prompt}

REPONSE EN FRANCAIS:"""

    # 2) appel Ollama
    try:
        res = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": full_prompt, "stream": False,
                  "options": {"num_predict": 500, "temperature": 0.2}},
            timeout=120
        )
        res.raise_for_status()
        data = res.json()

        # si Ollama renvoie error
        if "error" in data:
            return {"text": "", "error": data["error"], "layer": "FOG"}

        return {"text": data.get("response", ""), "layer": "FOG", "rag_used": rag is not None}

    except Exception as e:
        return {"text": "", "error": str(e), "layer": "FOG"}
