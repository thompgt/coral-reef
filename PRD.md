# Product Requirements Document: CoralMorph Search

**Version:** 1.0  
**Role:** Senior Product Manager / Lead Data Engineer  
**Status:** Initial Draft / Ready for Execution

---

## 1. Executive Summary & Goals
**CoralMorph Search** is a specialized semantic search engine designed to bridge the gap between technical marine biology data and natural language queries. Traditional keyword searches fail to capture the nuanced morphological descriptions used by researchers and enthusiasts. This application leverages modern NLP (Sentence-Transformers) and high-performance analytical storage (DuckDB) to enable vector-based similarity searches, allowing users to find species based on descriptive traits, habitats, and visual characteristics.

**Primary Goals:**
- Deliver sub-second semantic search latency.
- Provide a local-first, CPU-efficient ML architecture.
- Enable researchers to find species using "fuzzy" morphological descriptions.

---

## 2. User Stories
- **As a Marine Researcher:** I want to search for "branching structures with high calcification in deep lagoons" so I can identify potential species matches without knowing exact taxonomic names.
- **As a Recreational Diver:** I want to input "bright blue small polyps" to identify a coral I saw, even if the word "polyps" isn't the primary keyword in the database.
- **As a Data Engineer:** I want a lightweight, portable database (DuckDB) that handles both metadata and vector embeddings in a single file.

---

## 3. System Architecture
- **Text Embedding Engine:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vectors). Chosen for its balance of speed and semantic accuracy on CPU.
- **Storage & Search Layer:** **DuckDB**. 
    - Metadata stored in standard relational tables.
    - Vector embeddings stored as `FLOAT[]` or `BLOB`.
    - Similarity calculated via Cosine Similarity in SQL.
- **Backend API:** **FastAPI**.
    - Handles model loading (singleton pattern).
    - Manages DuckDB connection pool.
    - Exposes search and retrieval endpoints.
- **Frontend:** Single Page Application (SPA) using **Vanilla JS** and **Tailwind CSS**, communicating with the backend via JSON.

---

## 4. Data Pipeline & Ingestion
1.  **Cleaning:** Load `Coral_reef_data.csv`. Handle null values by replacing them with empty strings.
2.  **Feature Engineering:** Create a `search_text` column by concatenating features:
    `"Species: [Species Name]. Description: [Characters / Description]. Color: [Colour]. Habitat: [Habitat]. Abundance: [Abundance]."`
3.  **Embedding Generation:** Pass the `search_text` through the `all-MiniLM-L6-v2` model.
4.  **Persistence:**
    - Create a table `corals` in DuckDB.
    - Schema: `id (UUID/INT), species_name (VARCHAR), description (TEXT), colour (VARCHAR), habitat (VARCHAR), abundance (VARCHAR), embedding (FLOAT[384])`.
    - Use `COPY` or `INSERT` to populate the database.

---

## 5. API Specifications

### `GET /search`
- **Query Params:** 
    - `q` (string): The natural language query.
    - `limit` (int): Number of results (default: 10).
- **Processing:**
    1. Embed query `q` into a vector $v$.
    2. SQL Query: 
       ```sql
       SELECT species_name, description, color, habitat,
              list_cosine_similarity(embedding, $v) AS score
       FROM corals
       ORDER BY score DESC
       LIMIT $limit;
       ```
- **Response (200 OK):**
    ```json
    {
      "results": [
        {
          "species_name": "Acropora cervicornis",
          "score": 0.89,
          "metadata": { "color": "Brown/Tan", "habitat": "Fore reef" }
        }
      ]
    }
    ```

---

## 6. User Interface Requirements
- **Search Bar:** Centered, prominent input with an "Explore" button.
- **Results Grid:** Card-based layout showing `Species Name` as the title, a snippet of `Description`, and tags for `Color` and `Habitat`.
- **Visual Feedback:** 
    - Loading spinner during vector computation.
    - "No results found" state.
    - Similarity score indicator (e.g., "95% Match").
- **Styling:** Tailwind CSS with a "Marine" color palette (Blues, Teals, Aquas).

---

## 7. Implementation Phases

### Phase 1: Data & Embedding (The Engine)
- Script to process `Coral_reef_data.csv`.
- Benchmark embedding generation time.
- Initialize DuckDB and verify vector storage.

### Phase 2: Backend Core (The API)
- Implement FastAPI skeleton.
- Integrate Sentence-Transformers with a caching mechanism for the model.
- Write the DuckDB vector similarity SQL logic.

### Phase 3: Frontend Development (The Shell)
- Build the HTML/Tailwind search interface.
- Implement Fetch API calls to the backend.
- Handle responsive design for mobile/field use.

### Phase 4: Validation & Optimization
- **Validation Script:** Test query accuracy against known species traits.
- **Optimization:** Implement DuckDB indexing if dataset size exceeds 10k rows.
