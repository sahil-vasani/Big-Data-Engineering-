from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import sqlite3
import numpy as np
import os
import re

# =========================
# APP INIT
# =========================
app = FastAPI(title="Book Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# PATH CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DB_PATH = os.path.join(PROJECT_ROOT, "Database", "books.db")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "Embedding", "book_embeddings.npy")
MODEL_NAME = "all-MiniLM-L6-v2"

# =========================
# GLOBAL OBJECTS (LAZY)
# =========================
model = None    
embeddings = None
cosine_similarity = None

# =========================
# UTILS
# =========================
def parse_query(query):
    query = query.lower()
    k = 5
    if re.search(r"\b(one|1|single)\b", query): k = 1
    elif re.search(r"\b(two|2)\b", query): k = 2
    elif re.search(r"\b(three|3)\b", query): k = 3
    elif re.search(r"\b(top|best)\s+(\d+)\b", query):
        match = re.search(r"\b(top|best)\s+(\d+)\b", query)
        if match: k = int(match.group(2))

    clean_query = re.sub(
        r"\b(send|give|show|recommend|find|get|i want|me|book|books|which|is|are|to|about)\b",
        "",
        query
    )
    clean_query = re.sub(r"\s+", " ", clean_query).strip()
    return clean_query if len(clean_query) > 2 else query, k

def get_model_and_assets():
    global model, embeddings, cosine_similarity
    
    if model is None:
        print("⏳ Lazy loading model and assets...", flush=True)
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity as cs
        
        model = SentenceTransformer(MODEL_NAME, cache_folder="/tmp/hf_cache")
        embeddings = np.load(EMBEDDINGS_PATH, mmap_mode='r')
        cosine_similarity = cs
        print("✅ Assets loaded successfully.", flush=True)
    
    return model, embeddings, cosine_similarity

# =========================
# ENDPOINTS
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def serve_frontend():
    # Check if Frontend exists in root or relative to here
    frontend_path = os.path.join(PROJECT_ROOT, "Frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"error": "Frontend not found"}

# Mount static files correctly
frontend_dir = os.path.join(PROJECT_ROOT, "Frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/book/isbn/{isbn}")
def get_book_by_isbn(isbn: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE ISBN = ?", (isbn,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DescriptionRequest(BaseModel):
    description: str

@app.post("/recommend")
def recommend_books(request: DescriptionRequest):
    try:
        text = request.description.strip()
        if len(text) < 3:
            raise HTTPException(status_code=400, detail="Description too short")

        topic, k = parse_query(text)
        
        # Load assets on demand
        m, e, sim_func = get_model_and_assets()

        # Search
        query_vec = m.encode([topic])
        similarities = sim_func(query_vec, e)

        k = min(k, similarities.shape[1])
        top_indices = similarities[0].argsort()[-k:][::-1]
        row_ids = [int(i) + 1 for i in top_indices]
        
        # Fetch metadata from DB
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in row_ids)
        rows = conn.execute(f"SELECT *, rowid FROM books WHERE rowid IN ({placeholders})", row_ids).fetchall()
        conn.close()

        row_map = {row["rowid"]: dict(row) for row in rows}
        results = [row_map[idx] for idx in row_ids if idx in row_map]

        return {"query": text, "results": results}

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ ERROR: {e}\n{error_msg}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
