# =========================
# Lightweight Python base
# =========================
FROM python:3.10-slim

# =========================
# Environment settings
# =========================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/.cache
ENV HF_HOME=/app/.cache
ENV TORCH_HOME=/app/.cache

# =========================
# System dependencies
# =========================
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Working directory
# =========================
WORKDIR /app

# =========================
# Copy requirements first (cache-friendly)
# =========================
COPY requirements.txt .

# =========================
# Install Python deps (CPU ONLY)
# =========================
RUN pip install --no-cache-dir \
    torch==2.1.0+cpu \
    torchvision==0.16.0+cpu \
    torchaudio==2.1.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Copy project files
# =========================
COPY . .

# =========================
# Expose port
# =========================
EXPOSE 8000

# =========================
# Start FastAPI
# =========================
CMD ["uvicorn", "API.api:app", "--host", "0.0.0.0", "--port", "8000"]
