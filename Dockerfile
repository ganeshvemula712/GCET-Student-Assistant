# Use official Python 3.10 slim base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies file
COPY requirements.txt ./

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend ./backend

# Copy existing pre-indexed GCET vector database into a seed directory
# (Will populate persistent volume on first startup if volume is empty)
COPY chroma_db ./chroma_db_seed

# Expose container port
EXPOSE 8000

# Run startup script: Seed persistent volume if empty, then start Uvicorn (1 worker to prevent ChromaDB SQLite file lock contention)
CMD ["sh", "-c", "if [ ! -f /app/chroma_db/chroma.sqlite3 ] && [ -d /app/chroma_db_seed ]; then echo 'Seeding ChromaDB persistent volume...'; mkdir -p /app/chroma_db; cp -r /app/chroma_db_seed/* /app/chroma_db/; fi; uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
