from sentence_transformers import SentenceTransformer
import os

class ModelLoader:
    _instance = None

    @classmethod
    def get_model(cls):
        if cls._instance is None:
            print("🧠 Loading Sentence-Transformer (all-MiniLM-L6-v2) singleton...")
            cls._instance = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._instance
