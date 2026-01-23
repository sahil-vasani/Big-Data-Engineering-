from fastapi import FastAPI, HTTPException, Query
import sqlite3

app = FastAPI(
    title="Book Library API",
    description="API to fetch cleaned book data from SQLite",
    version="1.0.0"
)

DB_PATH = "db.sqlite3"


# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def root():
    return {"message": "Book Library API is working"}


# -----------------------------
# Get Latest Books
# -----------------------------
@app.get("/books")
def get_books(
    limit: int = Query(1000, ge=1, le=5000, description="Number of books to fetch")
):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM books
        WHERE description IS NOT NULL
        ORDER BY Acc_Date DESC
        LIMIT ?
    """, (limit,))

    books = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {
        "count": len(books),
        "data": books
    }


# -----------------------------
# Get Book by ISBN (Query Param)
# -----------------------------
@app.get("/book")
def get_book_by_isbn(
    isbn: str = Query(..., description="ISBN number of the book")
):
    isbn = isbn.strip().replace("-", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM books
        WHERE REPLACE(ISBN, '-', '') = ?
    """, (isbn,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return dict(row)


# -----------------------------
# Get Book by ISBN (Path Param)
# -----------------------------
@app.get("/books/{isbn}")
def get_book_by_isbn_path(isbn: str):
    isbn = isbn.strip().replace("-", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM books
        WHERE REPLACE(ISBN, '-', '') = ?
    """, (isbn,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return dict(row)
