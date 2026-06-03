from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import os
from typing import List, Optional
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI(title="CoralMorph Semantic Search API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "corals"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# Global Model Loader (Lazy Initialization)
class ModelLoader:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            print(f"🧠 Loading model: {MODEL_NAME}")
            cls._model = SentenceTransformer(MODEL_NAME)
        return cls._model

# Qdrant Client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

class SearchResult(BaseModel):
    species_name: str
    color: Optional[str]
    habitat: Optional[str]
    abundance: Optional[str]
    score: float
    description: Optional[str]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

@app.get("/api/search/", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="The natural language search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return")
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")

    try:
        # 1. Vectorize Query
        model = ModelLoader.get_model()
        query_vector = model.encode([q])[0].tolist()

        # 2. Search Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )

        # 3. Format Response
        formatted_results = []
        for hit in search_results:
            payload = hit.payload
            formatted_results.append(SearchResult(
                species_name=payload.get("species_name", "Unknown"),
                color=payload.get("color", ""),
                habitat=payload.get("habitat", ""),
                abundance=payload.get("abundance", ""),
                score=round(hit.score, 4),
                description=payload.get("description", "")
            ))

        return SearchResponse(query=q, results=formatted_results)

    except Exception as e:
        print(f"❌ Search Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during search: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME, "database": "Qdrant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
