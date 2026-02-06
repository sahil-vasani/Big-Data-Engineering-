import sqlite3
import pandas as pd
import os

# CSV PATH
CSV_PATH = "D:/COLLAGE/DAIICT/2 - SEM/BDE/Project/Big-Data-Engineering-/Data/processed/dau_with_description.csv"

# Read CSV
if not os.path.exists(CSV_PATH):
    print(f"❌ Error: CSV not found at {CSV_PATH}")
    exit(1)

df = pd.read_csv(CSV_PATH)

# SQLite connection
DB_FILE = os.path.join(os.path.dirname(__file__), "books.db")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Drop existing to rebuild
cursor.execute("DROP TABLE IF EXISTS books")

# Create table with book_url
cursor.execute("""
CREATE TABLE books (
    Acc_Date TEXT,
    Acc_No INTEGER PRIMARY KEY,
    Title TEXT,
    ISBN TEXT,
    Author_Editor TEXT,
    Edition_Volume TEXT,
    Place_Publisher TEXT,
    Year INTEGER,
    Pages TEXT,
    Class_No TEXT,
    description TEXT,
    image_url TEXT,
    book_url TEXT
)
""")

# Insert rows
print("⏳ Rebuilding database with URLs...")
for _, row in df.iterrows():
    cursor.execute("""
    INSERT OR IGNORE INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("Acc_Date"),
        int(row.get("Acc_No")) if pd.notnull(row.get("Acc_No")) else None,
        row.get("Title"),
        str(row.get("ISBN")),
        row.get("Author_Editor"),
        row.get("Edition_Volume"),
        row.get("Place_Publisher"),
        row.get("Year"),
        row.get("Pages"),
        row.get("Class_No"),
        row.get("description"),
        row.get("image_url"),
        row.get("book_url") # Now including the URL
    ))

conn.commit()
conn.close()

print("✅ Database successfully rebuilt with book_url!")
