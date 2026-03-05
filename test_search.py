import duckdb
from sentence_transformers import SentenceTransformer
import pandas as pd
import time

def test_semantic_search(query="spiky green branches in shallow water", top_k=5):
    print(f"🔍 Testing Semantic Search for: '{query}'")
    
    # 1. Load Model
    print("🧠 Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Vectorize Query
    start_embed = time.time()
    query_vector = model.encode([query])[0]
    embed_time = time.time() - start_embed
    
    # 3. Connect to DuckDB
    con = duckdb.connect('coral_morph.db')
    
    # 4. Perform Similarity Search
    sql = """
    SELECT 
        species_name, 
        color, 
        habitat, 
        list_cosine_similarity(embedding, ?) AS similarity_score,
        description
    FROM corals
    ORDER BY similarity_score DESC
    LIMIT ?
    """
    
    print("⚡ Querying DuckDB...")
    start_query = time.time()
    # Execute query and fetch as DataFrame
    df_results = con.execute(sql, [query_vector.tolist(), top_k]).fetchdf()
    query_time = time.time() - start_query
    
    # 5. Display Results
    print(f"\n✅ Found {len(df_results)} matches in {query_time:.4f}s (Embedding time: {embed_time:.4f}s):")
    print("-" * 80)
    for i, row in df_results.iterrows():
        print(f"Rank {i+1} | Score: {row['similarity_score']:.4f} | {row['species_name']}")
        print(f"   Color: {row['color']}")
        print(f"   Habitat: {row['habitat']}")
        print(f"   Snippet: {row['description'][:100]}...")
        print("-" * 80)
        
    con.close()

if __name__ == "__main__":
    test_semantic_search()
