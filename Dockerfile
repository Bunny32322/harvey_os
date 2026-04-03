# ── HARVEY OS Backend ──────────────────────────────────────────────────────
# Python 3.11 slim image for FastAPI + SQLite + ChromaDB
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ChromaDB and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data directory for SQLite + ChromaDB persistence
RUN mkdir -p /app/data

# Expose the port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
