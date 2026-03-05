# 🪸 CoralMorph Search

A semantic search engine for marine researchers to find coral species using natural language descriptions (e.g., "spiky green branches in shallow water").

## 🚀 Tech Stack
- **Backend:** Django + Django Rest Framework
- **Database:** DuckDB (Persistent vector storage)
- **ML Engine:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Frontend:** React + Tailwind CSS
- **Data:** Python (Pandas + PyArrow)

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

---

## 🧪 Testing
```bash
# Run Django unit tests
python manage.py test coral_api

# Run end-to-end validation script
python test_search.py
```
