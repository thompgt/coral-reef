import pandas as pd
import duckdb
from sentence_transformers import SentenceTransformer
import os
from tqdm import tqdm

def ingest_data(csv_path="Coral_reef_data.csv", db_path="coral_morph.db"):
    print("🚀 Initializing Ingestion Pipeline...")
    
    # 1. Load Data
    # The CSV has some odd column naming: 'Characters:', 'Description', 'Colour:', 'Color', etc.
    df = pd.read_csv(csv_path)
    
    # Mapping based on observed structure:
    # Column 0: Species Name
    # Column 3: Description
    # Column 5: Color
    # Column 7: Habitat
    # Column 9: Abundance
    
    # Let's rename columns by index to avoid confusion with duplicates/labels
    column_mapping = {
        df.columns[0]: "species_name",
        df.columns[3]: "description",
        df.columns[5]: "color",
        df.columns[7]: "habitat",
        df.columns[9]: "abundance"
    }
    
    df = df.rename(columns=column_mapping)
    df = df[["species_name", "description", "color", "habitat", "abundance"]]
    
    # Fill NaNs
    df = df.fillna("")

    # 2. Feature Engineering: Concatenate text for embedding
    print("📝 Engineering features...")
    df['search_text'] = (
        "Species: " + df["species_name"].astype(str) + ". " +
        "Description: " + df["description"].astype(str) + ". " +
        "Color: " + df["color"].astype(str) + ". " +
        "Habitat: " + df["habitat"].astype(str) + ". " +
        "Abundance: " + df["abundance"].astype(str)
    )

    # 3. Generate Embeddings
    print("🧠 Loading Sentence-Transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("⚡ Generating embeddings (this may take a minute on CPU)...")
    embeddings = model.encode(df['search_text'].tolist(), show_progress_bar=True)
    
    # 4. DuckDB Persistence
    print(f"💾 Persisting to DuckDB: {db_path}")
    con = duckdb.connect(db_path)
    
    # Create table with vector column
    con.execute("DROP TABLE IF EXISTS corals")
    con.execute("""
        CREATE TABLE corals (
            species_name VARCHAR,
            description TEXT,
            color VARCHAR,
            habitat VARCHAR,
            abundance VARCHAR,
            search_text TEXT,
            embedding FLOAT[]
        )
    """)
    
    # Prepare data for insertion
    df['embedding'] = embeddings.tolist()
    
    con.append('corals', df)
    
    con.close()
    print("✅ Ingestion complete!")

if __name__ == "__main__":
    ingest_data()
