# Big Data Engineering Project Workflow

## Project Overview
This project is a **Book Library Data Pipeline** that fetches book descriptions from multiple sources, stores them in a SQLite database, and exposes the data through a FastAPI REST API.

---

## Architecture & Workflow

### 1. **Data Collection & Enrichment** (`Data-Building/`)

#### Input
- **Source**: `dau_library_data.csv` - Raw library data with book metadata
  - Columns: Acc_Date, Acc_No, Title, ISBN, Author_Editor, Edition_Volume, Place_Publisher, Year, Pages, Class_No

#### Processing: `fetch_description.py`
This script enriches the raw data by fetching book descriptions from external sources.

**Steps:**
1. **Load & Clean Data**
   - Read CSV file (encoding: latin1)
   - Remove duplicate records based on: Title, ISBN, Author_Editor, Edition_Volume, Place_Publisher, Year, Pages, Class_No
   - Initialize description column with "Not Found"

2. **Fetch from OpenLibrary** (First Priority)
   - Iterate through books and clean ISBN numbers
   - Query: `https://openlibrary.org/isbn/{ISBN}`
   - Extract description from HTML element: `div.book-description div.read-more__content p`
   - Rate limit: 1 second delay per request
   - Fallback values: "ISBN Not Matched", "Description Not Available"

3. **Fetch from Google Books** (Second Priority)
   - For books still missing descriptions, query Google Books
   - Query: `https://books.google.com/books?vid=ISBN{ISBN}`
   - Extract synopsis from `<div id="synopsis">`
   - Rate limit: 0.2 second delay per request

#### Output
- **File**: `Data/processed/dau_with_description.csv`
- Contains all original columns + new `description` column

---

### 2. **Database Setup** (`Database/`)

#### Script: `SQLite3.py`
Loads the enriched CSV data into SQLite3 database.

**Process:**
1. Read: `Data/processed/dau_with_description.csv`
2. Create SQLite table `books` with schema:
   ```
   Acc_Date (TEXT)
   Acc_No (INTEGER, PRIMARY KEY)
   Title (TEXT)
   ISBN (INTEGER)
   Author_Editor (TEXT)
   Edition_Volume (TEXT)
   Place_Publisher (TEXT)
   Year (INTEGER)
   Pages (TEXT)
   Class_No (TEXT)
   description (TEXT)
   ```
3. Insert all rows with "INSERT OR IGNORE" (prevents duplicates)
4. Save to: `Database/db.sqlite3`

---

### 3. **REST API** (`API/`)

#### Script: `book_api.py`
FastAPI server that provides HTTP endpoints to query the book database.

**Technology Stack:**
- Framework: FastAPI
- Server: Uvicorn
- Database: SQLite3

**Endpoints:**

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|-----------|
| `/` | GET | Health check | - |
| `/books` | GET | Fetch books with descriptions | `limit` (1-5000, default: 1000) |
| `/book` | GET | Get book by ISBN (query param) | `isbn` (string, hyphens removed) |
| `/books/{isbn}` | GET | Get book by ISBN (path param) | `isbn` (string, hyphens removed) |

**Features:**
- Returns books ordered by `Acc_Date DESC` (most recent first)
- Only returns books that have descriptions (NOT NULL)
- ISBN comparison strips hyphens for flexible matching
- Returns 404 if book not found

---

## Full Data Pipeline Flow

```
dau_library_data.csv
        ↓
[Data-Building/fetch_description.py]
  - Remove duplicates
  - Fetch descriptions from OpenLibrary
  - Fetch descriptions from Google Books
        ↓
dau_with_description.csv
        ↓
[Database/SQLite3.py]
  - Load into SQLite3
  - Create books table
        ↓
db.sqlite3
        ↓
[API/book_api.py]
  - Start FastAPI server
  - Expose REST endpoints
        ↓
HTTP Clients
  - Query books via REST API
```

---

## File Structure

```
Big-Data-Engineering-/
├── API/
│   ├── book_api.py           # FastAPI REST server
│   └── __pycache__/
├── Data/
│   ├── raw_data/             # Original CSV files
│   │   └── dau_library_data.csv
│   └── processed/            # Enriched data
│       └── dau_with_description.csv
├── Data-Building/
│   ├── fetch_description.py  # Data enrichment script
│   └── load_data.ipynb       # Jupyter notebook for testing
├── Database/
│   ├── db.sqlite3            # SQLite database file
│   └── SQLite3.py            # Database loader script
├── logs/
│   └── prompt.md
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Dependencies

```
requests          # HTTP requests for OpenLibrary & Google Books
beautifulsoup4    # HTML parsing
fastapi           # REST API framework
pandas            # CSV data processing
uvicorn           # ASGI server for FastAPI
```

Install: `pip install -r requirements.txt`

---

## How to Run

### Step 1: Fetch Book Descriptions
```bash
cd Data-Building/
python fetch_description.py
# Output: Data/processed/dau_with_description.csv
```

### Step 2: Load Data into Database
```bash
cd Database/
python SQLite3.py
# Output: db.sqlite3
```

### Step 3: Start API Server
```bash
cd API/
uvicorn book_api:app --reload --host 0.0.0.0 --port 8000
# API available at: http://localhost:8000
```

### Step 4: Query the API
```bash
# Get 500 books with descriptions
curl http://localhost:8000/books?limit=500

# Get book by ISBN
curl http://localhost:8000/book?isbn=978-0-13-110362-7

# Get book by ISBN (path parameter)
curl http://localhost:8000/books/978-0-13-110362-7
```

---

## Key Considerations

### Data Quality
- Duplicate detection based on 8 fields to avoid redundant records
- Multiple fallback sources for descriptions (OpenLibrary → Google Books)
- Handles missing/malformed ISBNs gracefully

### Performance
- Rate limiting implemented (1s per OpenLibrary request, 0.2s per Google Books)
- Database queries indexed on primary key (Acc_No)
- Configurable result limit in API (max 5000 books)

### Error Handling
- HTTP request timeouts set to 10 seconds
- Missing descriptions marked as "Not Found" / "ISBN Not Matched" / "Description Not Available"
- API returns 404 for non-existent books
- INSERT OR IGNORE prevents database errors on duplicate keys

---

## Project Status & Next Steps

**Completed:**
- ✅ Data enrichment pipeline
- ✅ SQLite database schema & loader
- ✅ REST API with multiple query endpoints

**Potential Improvements:**
- Add authentication & rate limiting to API
- Implement caching for frequently accessed books
- Add pagination for large result sets
- Create admin endpoints for database management
- Add search functionality (title, author, ISBN)
- Set up logging & monitoring
- Create Docker container for deployment
