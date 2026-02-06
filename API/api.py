from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import sqlite3
import numpy as np
import pickle
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Reuse parser
from Embedding.book_recommender import parse_query

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
# PATH CONFIG (RELATIVE)
# =========================
DB_PATH = "Database/books.db"
EMBEDDINGS_PATH = "Embedding/book_embeddings.npy"
METADATA_PATH = "Embedding/books_metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

# =========================
# GLOBAL OBJECTS
# =========================
model = None    
embeddings = None

# =========================
# LAZY LOADING
# =========================
def get_model_and_embeddings():
    global model, embeddings
    if model is None:
        print("⏳ Lazy loading model...", flush=True)
        model = SentenceTransformer(MODEL_NAME, cache_folder="/tmp/hf_cache")
        print("✅ Model loaded.", flush=True)
    
    if embeddings is None:
        print("⏳ Lazy loading embeddings...", flush=True)
        # Use mmap_mode to save memory
        embeddings = np.load(EMBEDDINGS_PATH, mmap_mode='r')
        print("✅ Embeddings loaded.", flush=True)
    
    return model, embeddings

# REMOVED STARTUP EVENT


# =========================
# SERVE FRONTEND
# =========================
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("Frontend/index.html")

# =========================
# DATABASE UTILS
# =========================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# REQUEST SCHEMA
# =========================
class DescriptionRequest(BaseModel):
    description: str

# =========================
# ENDPOINT 1: ISBN SEARCH
# =========================
@app.get("/book/isbn/{isbn}")
def get_book_by_isbn(isbn: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE ISBN = ?", (isbn,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return dict(row)

# =========================
# ENDPOINT 2: ML RECOMMEND
# =========================
@app.post("/recommend")
def recommend_books(request: DescriptionRequest):
    try:
        text = request.description.strip()

        if len(text) < 3:
            raise HTTPException(status_code=400, detail="Description too short")

        parsed = parse_query(text)

        if isinstance(parsed, tuple):
            topic, k = parsed
        else:
            topic, k = parsed, 5

        # Ensure model is loaded
        model_instance, embeddings_instance = get_model_and_embeddings()

        # Encode query
        query_vec = model_instance.encode([topic])
        similarities = cosine_similarity(query_vec, embeddings_instance)

        # Get top k indices
        k = min(k, similarities.shape[1])
        top_indices = similarities[0].argsort()[-k:][::-1]

        # Convert 0-based numpy indices to 1-based SQLite rowids
        # Assumption: DB rows were inserted in same order as embeddings (create_db.py follows csv vs numpy save)
        row_ids = [int(i) + 1 for i in top_indices]
        
        # Fetch from DB
        conn = get_db_connection()
        placeholders = ",".join("?" for _ in row_ids)
        query = f"SELECT *, rowid FROM books WHERE rowid IN ({placeholders})"
        
        cursor = conn.execute(query, row_ids)
        rows = cursor.fetchall()
        conn.close()

        # Create a map for sorting
        row_map = {row["rowid"]: dict(row) for row in rows}
        
        results = []
        for idx in row_ids:
            if idx in row_map:
                row = row_map[idx]
                results.append({
                    "Acc_No": row["Acc_No"],
                    "Title": row["Title"],
                    "Author_Editor": row["Author_Editor"],
                    "ISBN": str(row["ISBN"]),
                    "Year": row["Year"],
                    "description": row["description"],
                    "image_url": row["image_url"]
                })

        return {
            "query": text,
            "results": results
        }

    except Exception as e:
        print("❌ ERROR IN /recommend:", repr(e), flush=True)
        raise HTTPException(status_code=500, detail="Internal recommendation error")
