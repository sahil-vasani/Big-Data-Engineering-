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
df = None

# =========================
# LOAD ONCE AT STARTUP
# =========================
@app.on_event("startup")
def load_assets():
    global model, embeddings, df

    print("🚀 Loading model, embeddings, and metadata...", flush=True)

    model = SentenceTransformer(
        MODEL_NAME,
        cache_folder="/tmp/hf_cache"
    )

    # Use mmap_mode to save memory (keeps file on disk, pages in as needed)
    embeddings = np.load(EMBEDDINGS_PATH, mmap_mode='r')

    with open(METADATA_PATH, "rb") as f:
        df = pickle.load(f)

    print("✅ Assets loaded successfully (no recomputation)", flush=True)


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

        query_vec = model.encode([topic])
        similarities = cosine_similarity(query_vec, embeddings)

        k = min(k, similarities.shape[1])
        top_indices = similarities[0].argsort()[-k:][::-1]

        results_df = df.iloc[top_indices]

        results = []
        for _, row in results_df.iterrows():
            results.append({
                "Acc_No": int(row["Acc_No"]) if not pd.isna(row["Acc_No"]) else None,
                "Title": str(row["Title"]),
                "Author_Editor": str(row["Author_Editor"]),
                "ISBN": str(row["ISBN"]),
                "Year": int(row["Year"]) if not pd.isna(row["Year"]) else None,
                "description": str(row["description"]),
                "image_url": str(row["image_url"]) if "image_url" in row else None
            })

        return {
            "query": text,
            "results": results
        }

    except Exception as e:
        print("❌ ERROR IN /recommend:", repr(e))
        raise HTTPException(status_code=500, detail="Internal recommendation error")
