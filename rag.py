import os
import mysql.connector
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class PatientRAG:
    def __init__(self):
        self.embedder = SentenceTransformer(
            os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
        )
        self.docs = []
        self.index = None
        self._build_index()

    def _get_patients(self):
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "root"),
            database=os.getenv("DB_NAME", "medical"),
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT patient_id, nom, prenom, age, sexe, maladies, traitement, dernier_diagnostic
            FROM patients
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def _build_index(self):
        patients = self._get_patients()

        self.docs = [
            f"Fiche Patient - ID: {p[0]}, Nom: {p[1]} {p[2]}, Age: {p[3]}, Sexe: {p[4]}, "
            f"Maladies: {p[5]}, Traitement: {p[6]}, Dernier diagnostic: {p[7]}"
            for p in patients
        ]

        emb = self.embedder.encode(self.docs, normalize_embeddings=True)
        emb = np.array(emb).astype("float32")

        self.index = faiss.IndexFlatIP(emb.shape[1])  # cosine via embeddings normalisés
        self.index.add(emb)

    def search(self, query: str, k: int = 2, min_score: float = 0.35) -> str:
        q_emb = self.embedder.encode([query], normalize_embeddings=True)
        q_emb = np.array(q_emb).astype("float32")

        scores, idxs = self.index.search(q_emb, k)

        best_score = float(scores[0][0])
        best_idx = int(idxs[0][0])

        if best_idx == -1 or best_score < min_score:
            return "Aucun dossier patient trouvé."

        # on peut concaténer top-k
        chosen = []
        for score, i in zip(scores[0], idxs[0]):
            if int(i) != -1 and float(score) >= min_score:
                chosen.append(self.docs[int(i)])
        return "\n---\n".join(chosen) if chosen else "Aucun dossier patient trouvé."
