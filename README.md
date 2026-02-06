# Big Data Engineering Project Workflow

## Project Overview
This project is a **Book Library Data Pipeline** that fetches book descriptions, generates semantic embeddings for recommendation, stores metadata in a SQLite database, and exposes the data through a FastAPI REST API.

---

## Architecture & Workflow

### 1. **Data Collection & Enrichment** (`Data-Building/`)
- **Script**: `fetch_description.py`
- **Input**: `dau_library_data.csv`
- **Process**: Fetches book descriptions from OpenLibrary and Google Books.
- **Output**: `Data/processed/dau_with_description.csv`

### **Data Statistics**
- **Initial Records**: 36,359
- **Unique Records** (after duplicate removal): 31,645
- **Cleaned Records** (after removing null Title, Author, Description): 26,009


### 2. **Embedding Generation** (`Embedding/`)
- **Script 1**: `book_recommender.py` (Run this first to verify logic/test)
- **Script 2**: `save_embeddings.py` (Run this to generate artifacts)
- **TIMELINE**:
    1. Loads `dau_with_description.csv`.
    2. Cleans text using NLTK.
    3. Uses `sentence-transformers` (all-MiniLM-L6-v2) to create vector embeddings for descriptions.
- **Output**:
    - `book_embeddings.npy` (Numpy array of vectors)
    - `books_metadata.pkl` (Pickled DataFrame with metadata)

### 3. **Database Setup** (`Database/`)
- **Script**: `create_db.py`
- **Process**: Loads `dau_with_description.csv` into a SQLite database.
- **Output**: `books.db`

### 4. **REST API** (`API/`)
- **Script**: `api.py`
- **Process**: Starts a FastAPI server that loads `books.db`, `book_embeddings.npy`, and `books_metadata.pkl`.
- **Features**:
    - Fetch book by ISBN
    - Semantic Search (Recommendation) based on description query
    - Frontend UI for book search and recommendations

---

## Full Data Pipeline Flow

```
dau_library_data.csv
        ↓
[Data-Building/fetch_description.py]
        ↓
dau_with_description.csv
    ↙          ↘
[Embedding/]    [Database/create_db.py]
    ↓                  ↓
save_embeddings.py   books.db
    ↓
book_embeddings.npy
books_metadata.pkl
        ↘           ↙
      [API/api.py]
           ↓
      REST API Server
```

---

## File Structure

```
Big-Data-Engineering-/
├── API/
│   ├── api.py                # FastAPI REST server
│   ├── __init__.py
│   └── __pycache__/
├── Data/
│   ├── raw_data/             # Original CSV files
│   └── processed/            # Enriched data
├── Data-Building/
│   ├── fetch_description.py  # Data enrichment script
│   └── load_data.ipynb
├── Database/
│   ├── create_db.py          # Database creation script
│   └── books.db              # Output Database
├── Embedding/
│   ├── book_recommender.py   # Recommender logic
│   ├── save_embeddings.py    # Script to save embeddings
│   ├── book_embeddings.npy   # Output Vector file
│   ├── books_metadata.pkl    # Output Metadata file
│   └── __pycache__/
├── Frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── logs/
│   └── prompt.md
├── requirements.txt          # Python dependencies
└── README.md
```

---

## Dependencies

```
requests              # HTTP requests for OpenLibrary & Google Books
beautifulsoup4        # HTML parsing for web scraping
fastapi               # REST API framework
pandas                # CSV data processing
uvicorn               # ASGI server for FastAPI
tqdm                  # Progress bars for data processing
urllib3               # HTTP client library
torch                 # Deep learning library (PyTorch)
gensim                # Word2Vec implementation
sentence-transformers # Transformer models for semantic embeddings
scikit-learn          # Cosine similarity calculation
nltk                  # Natural Language Processing (Tokenization)
numpy                 # Numerical operations and array handling
```

**Install all dependencies**:
```bash
pip install -r requirements.txt
```

**Download NLTK data** (required for text processing):
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

---

## How to Run

### Step 1: Fetch Book Descriptions
```bash
cd Data-Building/
python fetch_description.py
# Output: Data/processed/dau_with_description.csv
```

### Step 2: Generate Embeddings
First, you can run the recommender script to verify the logic:
```bash
cd Embedding/
python book_recommender.py
```
Then, save the embeddings and metadata for the API:
```bash
python save_embeddings.py
# Output: book_embeddings.npy, books_metadata.pkl
```

### Step 3: Create Database
```bash
cd Database/
python create_db.py
# Output: books.db
```

### Step 4: Start API Server
```bash
cd API/
uvicorn api:app --reload --host 0.0.0.0 --port 8000
# API available at: http://localhost:8000
# Frontend UI: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## API Endpoints

### 1. **GET /** 
**Description**: Serves the frontend web interface

**Response**: HTML page

**Example**:
```
http://localhost:8000/
```

---

### 2. **GET /book/isbn/{isbn}**
**Description**: Fetch book details by ISBN number

**Parameters**:
- `isbn` (path parameter): ISBN number of the book

**Response**:
```json
{
  "Acc_No": 12345,
  "Title": "Introduction to Algorithms",
  "Author_Editor": "Thomas H. Cormen",
  "ISBN": "9780262033848",
  "Year": 2009,
  "description": "A comprehensive textbook on algorithms...",
  "image_url": "https://example.com/cover.jpg"
}
```

**Error Responses**:
- `404`: Book not found

**Example**:
```bash
curl http://localhost:8000/book/isbn/9780262033848
```

---

### 3. **POST /recommend**
**Description**: Get book recommendations based on a description or topic query using semantic search with ML embeddings

**Request Body**:
```json
{
  "description": "machine learning and artificial intelligence"
}
```

**Response**:
```json
{
  "query": "machine learning and artificial intelligence",
  "results": [
    {
      "Acc_No": 12345,
      "Title": "Pattern Recognition and Machine Learning",
      "Author_Editor": "Christopher M. Bishop",
      "ISBN": "9780387310732",
      "Year": 2006,
      "description": "This leading textbook provides a comprehensive introduction...",
      "image_url": "https://example.com/cover.jpg"
    },
    {
      "Acc_No": 12346,
      "Title": "Artificial Intelligence: A Modern Approach",
      "Author_Editor": "Stuart Russell, Peter Norvig",
      "ISBN": "9780136042594",
      "Year": 2010,
      "description": "The most comprehensive, up-to-date introduction to AI...",
      "image_url": "https://example.com/cover2.jpg"
    }
  ]
}
```

**Features**:
- Uses `sentence-transformers` (all-MiniLM-L6-v2) model for semantic understanding
- Returns top 5 most similar books by default
- Query parsing: Can specify number of results (e.g., "machine learning [10]" returns 10 results)
- Cosine similarity scoring for ranking

**Error Responses**:
- `400`: Description too short (minimum 3 characters)
- `500`: Internal recommendation error

**Example**:
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"description": "data structures and algorithms"}'
```

---

## API Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Frontend

The project includes a web-based frontend interface:
- **Location**: `Frontend/` directory
- **Files**: `index.html`, `script.js`, `style.css`
- **Access**: http://localhost:8000/ (served automatically by the API)
- **Features**:
  - Search books by ISBN
  - Get AI-powered book recommendations
  - View book details including cover images
