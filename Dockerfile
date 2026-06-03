# Use Python 3.12 slim for a smaller image size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for DuckDB/Torch/Pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the model to cache it in the image layer
# This prevents downloading it every time the container starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the application (FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
