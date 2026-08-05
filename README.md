# 🪸 CoralMorph Search

A semantic search engine for marine researchers to find coral species using natural language descriptions (e.g., "spiky green branches in shallow water").

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?style=for-the-badge&logo=qdrant&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## 📓 Live Demo (Jupyter Notebook)

`Demo.ipynb` is a self-contained, runnable walkthrough of the whole project — no Qdrant/DuckDB server required. It loads the real `Coral_reef_data.csv`, embeds every species with the actual `all-MiniLM-L6-v2` production model, and runs genuine cosine-similarity search against those embeddings (mathematically identical to what Qdrant/DuckDB compute, just without the extra infrastructure). It includes:

- EDA over the raw dataset (description lengths, habitats, color terms).
- Real semantic search vs. a TF-IDF lexical baseline, compared side by side.
- A **live, interactive search widget** (`ipywidgets`) you can type queries into.
- A 2D PCA visualization of the embedding space (Plotly), colored by habitat.
- K-means clustering of species by embedding, and a "species similar to X" nearest-neighbor explorer.
- A latency benchmark against the PRD's sub-second search goal.
- A `main.py`-style API response simulation, plus an automated validation suite mirroring `e2e_test.py`.

To run it:
```bash
pip install -r requirements.txt scikit-learn matplotlib plotly ipywidgets jupyter
jupyter notebook Demo.ipynb
```

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### 2. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Data Pipeline
The application requires the data to be processed and vectorized before the search engine can work.
```bash
# 1. Clean and prepare the CSV data
python data_preparation.py

# 2. Generate embeddings and store in DuckDB
python vectorize_and_store.py
```

### 4. Running the Backend
```bash
# Start the Django development server
python manage.py runserver
```
The API will be available at `http://localhost:8000/api/search/?q=your_query`.

### 5. Running the Frontend
```bash
cd frontend
npm install
npm run dev
```
The UI will be available at `http://localhost:5173`.

---

## 🔍 API Usage

### `GET /api/search/`
**Parameters:**
- `q`: The natural language search query.
- `limit` (optional): Number of results to return (default: 10).

**Example Response:**
```json
{
  "query": "shallow green coral",
  "results": [
    {
      "species_name": "Acropora pruinosa",
      "score": 0.468,
      "color": "Greenish and brown",
      "habitat": "Shallow turbid water",
      "description": "..."
    }
  ]
}
```

### Error Response Format
All API errors now return a consistent payload:

```json
{
  "error": {
    "code": "MISSING_QUERY",
    "message": "Query parameter 'q' is required.",
    "details": {
      "parameter": "q"
    }
  }
}
```

### Rate Limiting and Caching
The search API includes built-in request throttling and response caching.

- Rate limiting:
  - Anonymous clients: `60/minute` (default)
  - Authenticated clients: `120/minute` (default)
- Search response cache:
  - Cached by `(query, limit)` key
  - Default TTL: `300` seconds

You can tune these values with environment variables:

```bash
SEARCH_ANON_RATE=60/minute
SEARCH_USER_RATE=120/minute
SEARCH_CACHE_TTL=300
CACHE_DEFAULT_TIMEOUT=300
CACHE_MAX_ENTRIES=1000
```

When throttled, the API returns:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many search requests. Please try again shortly.",
    "details": {
      "wait_seconds": 12
    }
  }
}
```

---

## 🧪 Testing
```bash
# Run Django unit tests
python manage.py test coral_api

# Run end-to-end validation script
python test_search.py
```
