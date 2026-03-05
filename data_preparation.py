import pandas as pd
import numpy as np
import re
import os

def clean_text(text):
    """Basic text cleaning: remove extra whitespace and standardize formatting."""
    if pd.isna(text) or text == "":
        return "Not specified"
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', str(text)).strip()
    return text

def prepare_coral_data(input_path="Coral_reef_data.csv", output_path="cleaned_coral_data.parquet"):
    print(f"🛠️ Starting data preparation for {input_path}...")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found.")
        return

    # 1. Load Data
    # The dataset has non-UTF-8 characters (e.g. 0x91 for curly quotes).
    # Using 'ISO-8859-1' encoding to ensure robust loading.
    df = pd.read_csv(input_path, encoding='ISO-8859-1')
    
    # 2. Strategic Column Mapping
    # The CSV has labels in alternating columns. We extract the actual data columns.
    column_mapping = {
        df.columns[0]: "species_name",
        df.columns[3]: "description",
        df.columns[5]: "color",
        df.columns[7]: "habitat",
        df.columns[9]: "abundance"
    }
    df = df.rename(columns=column_mapping)
    df = df[["species_name", "description", "color", "habitat", "abundance"]]

    # 3. Handle Nulls and Standardize Text
    print("🧹 Cleaning text and handling null values...")
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # 4. Feature Engineering
    print("🧪 Engineering semantic features...")
    
    # Metadata feature: Description length (useful for filtering/sorting)
    df['description_length'] = df['description'].apply(len)
    
    # Feature: Structured Search Text
    # This is the 'gold' feature for the Sentence-Transformer.
    # We use a structured prompt-like format to help the model understand context.
    df['search_text'] = (
        "Species: " + df["species_name"] + ". " +
        "Physical Traits: " + df["description"] + ". " +
        "Visual Appearance: " + df["color"] + ". " +
        "Natural Habitat: " + df["habitat"] + ". " +
        "Population Status: " + df["abundance"] + "."
    )
    
    # Feature: Primary Habitat (Extraction of first listed habitat for categorization)
    df['primary_habitat'] = df['habitat'].str.split(',').str[0].str.split(';').str[0].str.strip()

    # 5. Scaling/Normalization (Note: Primary features are text, but we'll scale metadata if needed)
    # If we had depth or numerical data, we would use StandardScaler here.
    # For now, we'll ensure the description_length is normalized for potential UI ranking.
    max_len = df['description_length'].max()
    df['normalized_desc_length'] = df['description_length'] / max_len if max_len > 0 else 0

    # 6. Final Inspection
    print(f"📊 Preparation complete. Total species processed: {len(df)}")
    print(df[["species_name", "primary_habitat", "description_length"]].head())

    # 7. Save for Downstream Consumption
    # Parquet is preferred for DuckDB ingestion due to type preservation.
    df.to_parquet(output_path, index=False)
    print(f"💾 Cleaned data saved to: {output_path}")

if __name__ == "__main__":
    # Ensure pyarrow is installed for parquet support
    try:
        import pyarrow
    except ImportError:
        print("📦 Installing pyarrow for efficient data storage...")
        os.system("pip install pyarrow")
        
    prepare_coral_data()
