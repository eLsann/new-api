# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install basic system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Create data directories
RUN mkdir -p data/snapshots

# Expose port (Fly.io uses internal port 8080)
EXPOSE 8080

# Start command for Fly.io
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
