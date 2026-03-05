import pandas as pd
import duckdb
from sentence_transformers import SentenceTransformer
import os
import time

def vectorize_and_store(input_path="cleaned_coral_data.parquet", db_path="coral_morph.db"):
    print(f"🚀 Starting Vectorization & Storage Pipeline...")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found. Please run data_preparation.py first.")
        return

    # 1. Load Cleaned Data
    print(f"📖 Loading cleaned data from {input_path}...")
    df = pd.read_parquet(input_path)
    
    # 2. Initialize Sentence Transformer
    # Using 'all-MiniLM-L6-v2' for a balance of speed and performance on CPU
    print("🧠 Loading Sentence-Transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 3. Generate Embeddings
    print(f"⚡ Generating embeddings for {len(df)} species (this may take a moment)...")
    start_time = time.time()
    
    # model.encode returns a numpy array
    embeddings = model.encode(df['search_text'].tolist(), show_progress_bar=True)
    
    # Convert embeddings to a list of lists for DuckDB compatibility
    df['embedding'] = embeddings.tolist()
    
    duration = time.time() - start_time
    print(f"✅ Vectorization complete in {duration:.2f} seconds.")

    # 4. DuckDB Persistence
    print(f"💾 Connecting to DuckDB: {db_path}")
    con = duckdb.connect(db_path)
    
    # Create the table schema
    # We include all metadata columns plus the vector embedding
    con.execute("DROP TABLE IF EXISTS corals")
    con.execute("""
        CREATE TABLE corals (
            species_name VARCHAR,
            description TEXT,
            color VARCHAR,
            habitat VARCHAR,
            abundance VARCHAR,
            description_length INTEGER,
            search_text TEXT,
            primary_habitat VARCHAR,
            normalized_desc_length DOUBLE,
            embedding FLOAT[]
        )
    """)
    
    # Insert data from the pandas DataFrame
    print("📥 Inserting data into 'corals' table...")
    con.append('corals', df)
    
    # 5. Verify and Index
    count = con.execute("SELECT count(*) FROM corals").fetchone()[0]
    print(f"✨ Successfully stored {count} records in {db_path}.")
    
    con.close()
    print("🏁 Pipeline finished successfully!")

if __name__ == "__main__":
    vectorize_and_store()
