from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from core.platform import Platform
from core.runner import Runner

app = FastAPI(title="LLM Dispatcher Gateway")

# CORS (important pour appeler depuis la PWA)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # pour la démo (en prod tu limites)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

platform = Platform()
runner = Runner(platform)

class DispatchReq(BaseModel):
    prompt: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/dispatch")
def dispatch(req: DispatchReq):
    return runner.dispatch(req.prompt)
