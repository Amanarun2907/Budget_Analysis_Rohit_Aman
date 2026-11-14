# ==============================================================================
# Multi-stage Dockerfile for Budget Intelligence Platform
# ==============================================================================

# Stage 1: Build the Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.12-slim AS runner
WORKDIR /app

# Install system dependencies (Poppler and Tesseract OCR if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy Backend Code
COPY backend/ ./backend/

# Copy built frontend assets to frontend/dist for FastAPI StaticFiles mount
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create runtime directories
RUN mkdir -p /app/backend/uploads /app/backend/reports /app/backend/chroma_db

WORKDIR /app/backend

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
