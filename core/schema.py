# core/schema.py

import os


MODELS_SCHEMA = {
    "edge": {
        "model": "phi3:latest",
        "url": "http://localhost:11434/api/generate"
    },
    "fog": {
        "model": "phi3:latest",
        "url": "http://localhost:8001/generate"
    },
     "cloud": {
      "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
      "api_key": os.getenv("OPENAI_API_KEY", "")
    }
}

# Kelmat complexity (Route to Cloud)
COMPLEX_MARKERS = ["analyse", "compare", "mécanisme", "biochimie", "impact", "synthèse", "pharmacologie", "traitement", "maladie"]

# Kelmat RAG (Route to Fog)
RAG_MARKERS = ["patient", "id:", "dossier", "fiche", "historique", "diagnostic de"]

PHI_PATTERNS = {
    "phone": r"\b(\+?\d[\d\s\-]{7,}\d)\b",
    "id": r"\b(ID-|id-)?\d{4}\b", # Matching patient_id dyalk (4 digits)
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
}