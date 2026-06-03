import pandas as pd
import os
import time
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

def vectorize_and_store(input_path="cleaned_coral_data.parquet"):
    print(f"🚀 Starting Vectorization & Storage Pipeline for Qdrant...")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found. Please run data_preparation.py first.")
        return

    # 1. Load Cleaned Data
    print(f"📖 Loading cleaned data from {input_path}...")
    df = pd.read_parquet(input_path)
    
    # 2. Initialize Sentence Transformer
    print("🧠 Loading Sentence-Transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 3. Generate Embeddings
    print(f"⚡ Generating embeddings for {len(df)} species...")
    start_time = time.time()
    embeddings = model.encode(df['search_text'].tolist(), show_progress_bar=True)
    duration = time.time() - start_time
    print(f"✅ Vectorization complete in {duration:.2f} seconds.")

    # 4. Qdrant Persistence
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    print(f"💾 Connecting to Qdrant at {host}:{port}...")
    client = QdrantClient(host=host, port=port)
    
    collection_name = "corals"
    
    # Recreate the collection (drops if exists)
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    
    print(f"📥 Preparing points for upsert into '{collection_name}' collection...")
    points = []
    for idx, row in df.iterrows():
        # Metadata payload (all columns except the one we might have added for internal use)
        payload = row.to_dict()
        
        points.append(PointStruct(
            id=idx,
            vector=embeddings[idx].tolist(),
            payload=payload
        )
    )
    
    # Batch upsert
    client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )
    
    # 5. Verification
    collection_info = client.get_collection(collection_name=collection_name)
    print(f"✨ Successfully stored {collection_info.points_count} records in Qdrant.")
    print("🏁 Pipeline finished successfully!")

if __name__ == "__main__":
    vectorize_and_store()
