import sqlite3
import pandas as pd

# CSV PATH
CSV_PATH = "D:/COLLAGE/DAIICT/2 - SEM/BDE/Project/Big-Data-Engineering-/Data/processed/dau_with_description.csv"

# Read CSV
df = pd.read_csv(CSV_PATH)

# SQLite connection
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
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
    image_url TEXT
)
""")

# Insert rows
for _, row in df.iterrows():
    cursor.execute("""
    INSERT OR IGNORE INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("Acc_Date"),
        int(row.get("Acc_No")),
        row.get("Title"),
        str(row.get("ISBN")),
        row.get("Author_Editor"),
        row.get("Edition_Volume"),
        row.get("Place_Publisher"),
        row.get("Year"),
        row.get("Pages"),
        row.get("Class_No"),
        row.get("description"),
        row.get("image_url")
    ))

conn.commit()
conn.close()

print("✅ CSV successfully stored in SQLite database (books.db)")
