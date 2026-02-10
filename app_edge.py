import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from rag import PatientRAG

app = FastAPI()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "phi3")

rag = None

class PromptRequest(BaseModel):
    prompt: str

@app.on_event("startup")
def startup():
    global rag
    rag = PatientRAG()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate(req: PromptRequest):
    context = rag.search(req.prompt, k=2)

    full_prompt = f"""Tu es un assistant médical professionnel.
Utilise UNIQUEMENT la fiche patient ci-dessous pour répondre.
Si l'information n'est pas présente, dis clairement "Information non disponible dans la fiche".

FICHE PATIENT:
{context}

QUESTION:
{req.prompt}

REPONSE EN FRANCAIS:"""

    res = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {"num_predict": 500, "temperature": 0.2}
        },
        timeout=120
    )
    return {"text": res.json().get("response", ""), "layer": "FOG", "rag_used": True}
