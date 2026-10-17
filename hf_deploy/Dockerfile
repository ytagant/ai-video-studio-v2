# AI Video Studio — single-container deployment.
# Backend (FastAPI) serves both the API and the built frontend.
# Run: docker build -t video-studio . && docker run -p 7860:7860 -e GEMINI_API_KEY=... video-studio

# ---------- Stage 1: build the Next.js frontend (static export) ----------
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build   # -> out/  (output: 'export' in next.config.js)

# ---------- Stage 2: Python backend + ffmpeg ----------
FROM python:3.11-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
# keep jobs outside the image layers so videos persist per-container
RUN mkdir -p jobs
COPY --from=frontend /app/frontend/out ./static
ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
