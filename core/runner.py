# core/runner.py
import re
from core.schema import COMPLEX_MARKERS, RAG_MARKERS, PHI_PATTERNS

class Runner:
    def __init__(self, platform):
        self.platform = platform

    def contains_phi(self, prompt: str) -> bool:
        # PII Detection (Phone, Email, names etc)
        for pattern in PHI_PATTERNS.values():
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        return False

    def needs_rag(self, prompt: str) -> bool:
        # Check for 4-digit IDs (like 2102) or RAG keywords
        has_id = bool(re.search(r"\b\d{4}\b", prompt))
        has_rag_word = any(word in prompt.lower() for word in RAG_MARKERS)
        return has_id or has_rag_word

    def is_complex(self, prompt: str) -> bool:
        score = sum(1 for word in COMPLEX_MARKERS if word in prompt.lower())
        return score >= 1 or len(prompt) > 200

    def dispatch(self, prompt: str) -> dict:
        has_phi = self.contains_phi(prompt)
        is_rag = self.needs_rag(prompt)
        is_hard = self.is_complex(prompt)

        # 1. Privacy First -> Edge
        if has_phi and not is_rag: 
            res = self.platform.call_edge(prompt)
            res["reason"] = "🔒 Privacy Shield: Data stays on Edge"
            return res

        # 2. RAG Needs -> Fog (with Privacy)
        if is_rag:
            try:
                res = self.platform.call_fog(prompt)
                res["reason"] = "📂 Patient Context Found -> Fog (Secure)"
                return res
            except:
                res = self.platform.call_edge(prompt)
                res["reason"] = "⚠️ Fog Fallback to Edge"
                return res

        # 3. Scientific / General Question -> Cloud
        if is_hard:
            res = self.platform.call_cloud(prompt)
            res["reason"] = "⚡ High-Level Analysis -> Cloud (GPT)"
            return res

        # 4. Simple Task
        res = self.platform.call_edge(prompt)
        res["reason"] = "🚀 Simple Task -> Local Edge"
        return res