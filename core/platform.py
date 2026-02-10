# core/platform.py
import time
import requests
from openai import OpenAI
from core.schema import MODELS_SCHEMA

class Platform:
    def __init__(self):
        self.schema = MODELS_SCHEMA

    def call_edge(self, prompt: str) -> dict:
        t0 = time.perf_counter()
        r = requests.post(
            self.schema["edge"]["url"],
            json={"model": self.schema["edge"]["model"], "prompt": prompt, "stream": False, "options": {"num_predict": 200}},
            timeout=40
        )
        return {"layer": "EDGE", "latency_ms": round((time.perf_counter()-t0)*1000, 2), "text": r.json().get("response", "")}

    def call_fog(self, prompt: str) -> dict:
        t0 = time.perf_counter()
        r = requests.post(self.schema["fog"]["url"], json={"prompt": prompt}, timeout=120)
        r.raise_for_status()
        data = r.json()

        return {
            "layer": "FOG",
            "latency_ms": round((time.perf_counter()-t0)*1000, 2),
            "text": data.get("text", ""),
            "fog_error": data.get("error", None)
        }

    def call_cloud(self, prompt: str) -> dict:
        t0 = time.perf_counter()
        client = OpenAI(api_key=self.schema["cloud"]["api_key"])
        response = client.chat.completions.create(
            model=self.schema["cloud"]["model"],
            messages=[
                {"role": "system", "content": "Tu es un expert en pharmacologie et médecine. Donne des analyses biochimiques détaillées."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return {"layer": "CLOUD", "latency_ms": round((time.perf_counter()-t0)*1000, 2), "text": response.choices[0].message.content}