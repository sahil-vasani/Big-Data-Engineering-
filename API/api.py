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

# =========================
# APP INIT
# =========================
app = FastAPI(title="Book Library API")

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
# UTILS (MATCHING USER SCRIPT)
# =========================

def parse_query(query):
    query = query.lower()
    k = 5

    # Quantity detection
    if re.search(r"\b(one|1|single)\b", query):
        k = 1
    elif re.search(r"\b(two|2)\b", query):
        k = 2
    elif re.search(r"\b(three|3)\b", query):
        k = 3
    elif re.search(r"\b(top|best)\s+(\d+)\b", query):
        match = re.search(r"\b(top|best)\s+(\d+)\b", query)
        if match:
            k = int(match.group(2))

    # Filler word removal (Mirroring user's script exactly)
    clean_query = re.sub(
        r"\b(send|give|show|recommend|find|get|i want|me|book|books|which|is|are|to|about)\b",
        "",
        query
    )
    clean_query = re.sub(r"\s+", " ", clean_query).strip()

    # Fallback to full query if cleaning makes it empty
    return (clean_query if len(clean_query) > 2 else query), k

def get_model_and_assets():
    global model, embeddings, cosine_similarity
    
    if model is None:
        print("⏳ Lazy loading SentenceTransformer...", flush=True)
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity as cs
        
        # Load model to CPU to save Railway memory
        model = SentenceTransformer(MODEL_NAME, cache_folder="/tmp/hf_cache", device="cpu")
        embeddings = np.load(EMBEDDINGS_PATH, mmap_mode='r')
        cosine_similarity = cs
        print("✅ Model and Embeddings Ready.", flush=True)
    
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

frontend_dir = os.path.join(PROJECT_ROOT, "Frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

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
            raise HTTPException(status_code=400, detail="Query too short")

        # Parse query using your script's logic
        topic, k = parse_query(raw_text)
        print(f"🔍 Searching: '{topic}' | Top-{k}", flush=True)
        
        # Load assets
        m, e, sim_func = get_model_and_assets()

        # 1. GENERATE QUERY VECTOR
        query_vec = m.encode([topic])
        
        # 2. CALCULATE COSINE SIMILARITY
        similarities = sim_func(query_vec, e)[0]

        # 3. GET TOP K INDICES
        # We use your logic: sort descending and pick k
        top_indices = similarities.argsort()[-k:][::-1]
        
        # Indices are 0-based, rowids in DB are 1-based (order must match)
        row_ids = [int(i) + 1 for i in top_indices]
        
        # 4. FETCH DATA FROM SQLITE
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in row_ids)
        query = f"SELECT *, rowid AS r_id FROM books WHERE rowid IN ({placeholders})"
        rows = conn.execute(query, row_ids).fetchall()
        conn.close()

        # Map results back to original sort order
        row_map = {row["r_id"]: dict(row) for row in rows}
        results = []
        for rid in row_ids:
            if rid in row_map:
                results.append(row_map[rid])

        return {"query": topic, "results": results}

    except Exception as e:
        print(f"❌ ERROR: {e}\n{traceback.format_exc()}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
