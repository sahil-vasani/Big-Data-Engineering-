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
    query = query.lower().strip()
    
    # Extract k (quantity)
    k = 5
    if re.search(r"\b(one|1|single)\b", query): k = 1
    elif re.search(r"\b(two|2)\b", query): k = 2
    elif re.search(r"\b(three|3)\b", query): k = 3
    elif re.search(r"\b(top|best|show)\s+(\d+)\b", query):
        match = re.search(r"\b(top|best|show)\s+(\d+)\b", query)
        if match: k = int(match.group(2))

    # Clean query for semantic search - remove only filler phrases
    clean_query = re.sub(
        r"\b(send|give|show|recommend|find|get|i want|me|book|books|which|is|are|to|highly|correlated|related)\b",
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
        
        # Use CPU-friendly settings
        model = SentenceTransformer(MODEL_NAME, cache_folder="/tmp/hf_cache", device="cpu")
        # Embeddings are (26009, 384)
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
        text = request.description.strip()
        if len(text) < 2:
            raise HTTPException(status_code=400, detail="Query too short")

        topic, k = parse_query(text)
        
        # Load assets
        m, e, sim_func = get_model_and_assets()

        # 1. SEMANTIC SEARCH
        query_vec = m.encode([topic])
        similarities = sim_func(query_vec, e)[0]

        # Get a larger pool (e.g., 50) to allow for re-ranking
        pool_size = max(50, k * 2)
        top_indices = similarities.argsort()[-pool_size:][::-1]
        
        # indices are 0-based, rowids are 1-based
        row_ids = [int(i) + 1 for i in top_indices]
        
        # 2. FETCH FROM DB
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in row_ids)
        query = f"SELECT *, rowid AS r_id FROM books WHERE rowid IN ({placeholders})"
        rows = conn.execute(query, row_ids).fetchall()
        conn.close()

        # Map results
        row_map = {row["r_id"]: dict(row) for row in rows}
        
        # 3. HYBRID RE-RANKING (Semantic + Keyword Boost)
        # We boost books where query terms appear in the Title
        keywords = set(topic.lower().split())
        
        scored_results = []
        for idx in top_indices:
            r_id = int(idx) + 1
            if r_id not in row_map:
                continue
                
            book = row_map[r_id]
            title = book.get("Title", "").lower()
            
            # Base score is semantic similarity
            score = float(similarities[idx])
            
            # Boost score if keywords are in title
            matches = sum(1 for word in keywords if word in title and len(word) > 2)
            if matches > 0:
                # Significant boost for title matches
                score += 0.2 * matches 
            
            scored_results.append((score, book))

        # Re-sort by final score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Take final k
        final_results = [item[1] for item in scored_results[:k]]

        return {"query": topic, "results": final_results}

    except Exception as e:
        print(f"❌ ERROR: {e}\n{traceback.format_exc()}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
