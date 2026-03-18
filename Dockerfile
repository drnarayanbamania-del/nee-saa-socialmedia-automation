# Multi-stage Dockerfile for Hindi AI Automation Platform

# Stage 1: Backend and AI Engine
FROM python:3.11-slim as backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and AI engine code
COPY backend/ ./backend/
COPY ai_engine/ ./ai_engine/
COPY scraper/ ./scraper/
COPY automation/ ./automation/
COPY main_coordinator.py ./

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "backend/main.py"]

# Stage 2: Frontend (for static files)
FROM node:18-alpine as frontend

WORKDIR /frontend
COPY frontend/ ./

# Stage 3: Production
FROM python:3.11-slim as production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagagick \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy from backend stage
COPY --from=backend /app /app
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy frontend
COPY --from=frontend /frontend /app/frontend

# Create directories for outputs
RUN mkdir -p /app/outputs /app/generated_images /app/temp_audio /app/final_videos /app/thumbnails && \
    chown -R 1000:1000 /app

# Switch to non-root user
USER 1000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "backend/main.py"]