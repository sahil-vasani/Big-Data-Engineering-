from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import sqlite3
import numpy as np
import os
import re
import traceback
import random

# =========================
# APP INIT
# =========================
app = FastAPI(title="Elegant Library Recommendation Engine")

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
    k = 12 # Default increased to 12 for better UI grid layout

    # Quantity detection
    if re.search(r"\b(one|1|single)\b", query): k = 1
    elif re.search(r"\b(two|2)\b", query): k = 2
    elif re.search(r"\b(three|3)\b", query): k = 3
    elif re.search(r"\b(top|best)\s+(\d+)\b", query):
        match = re.search(r"\b(top|best)\s+(\d+)\b", query)
        if match: k = int(match.group(2))

    # Filler word removal (User's logic)
    clean_query = re.sub(
        r"\b(send|give|show|recommend|find|get|i want|me|book|books|which|is|are|to|about)\b",
        "",
        query
    )
    clean_query = re.sub(r"\s+", " ", clean_query).strip()

    return (clean_query if len(clean_query) > 2 else query), k

def get_model_and_assets():
    global model, embeddings, cosine_similarity
    
    if model is None:
        print("⏳ Lazy loading assets...", flush=True)
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity as cs
        
        model = SentenceTransformer(MODEL_NAME, cache_folder="/tmp/hf_cache", device="cpu")
        embeddings = np.load(EMBEDDINGS_PATH, mmap_mode='r')
        cosine_similarity = cs
        print("✅ Ready.", flush=True)
    
    return model, embeddings, cosine_similarity

# =========================
# ENDPOINTS
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def serve_frontend():
    frontend_path = os.path.join(PROJECT_ROOT, "Frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"error": "Frontend not found"}

# Move static mount after root to avoid priority issues if needed
frontend_dir = os.path.join(PROJECT_ROOT, "Frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/random")
def get_random_books():
    """Returns 12 random books for the initial UI display."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Get count first
        total = conn.execute("SELECT count(*) FROM books").fetchone()[0]
        # Pick 12 random indices
        random_indices = random.sample(range(1, total + 1), min(12, total))
        
        placeholders = ",".join("?" for _ in random_indices)
        query = f"SELECT *, rowid AS r_id FROM books WHERE rowid IN ({placeholders})"
        rows = conn.execute(query, random_indices).fetchall()
        conn.close()
        
        return {"results": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/book/isbn/{isbn}")
def get_book_by_isbn(isbn: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT *, rowid AS r_id FROM books WHERE ISBN = ?", (isbn,))
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
        raw_text = request.description.strip()
        if len(raw_text) < 2:
            return {"query": raw_text, "results": []}

        topic, k_requested = parse_query(raw_text)
        # Ensure we return at least a full row (4) and up to 20
        k = max(k_requested, 12) 
        
        m, e, sim_func = get_model_and_assets()

        query_vec = m.encode([topic])
        similarities = sim_func(query_vec, e)[0]

        # Get top indices
        top_indices = similarities.argsort()[-k:][::-1]
        row_ids = [int(i) + 1 for i in top_indices]
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in row_ids)
        query = f"SELECT *, rowid AS r_id FROM books WHERE rowid IN ({placeholders})"
        rows = conn.execute(query, row_ids).fetchall()
        conn.close()

        row_map = {row["r_id"]: dict(row) for row in rows}
        results = []
        for rid in row_ids:
            if rid in row_map:
                book = row_map[rid]
                # Add a simulated match percentage for UI
                idx_local = rid - 1
                if idx_local < len(similarities):
                     book["match_percent"] = int(similarities[idx_local] * 100)
                else:
                     book["match_percent"] = random.randint(70, 95)
                results.append(book)

        return {"query": topic, "results": results}

    except Exception as e:
        print(f"❌ ERROR: {e}\n{traceback.format_exc()}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
