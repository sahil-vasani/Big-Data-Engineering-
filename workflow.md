# 📘 Big Data Engineering Project Workflow

## Complete Step-by-Step Guide for Users

This document provides a comprehensive workflow for anyone who wants to use, understand, or replicate this Big Data Engineering project focused on book description enrichment.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Workflow Steps](#workflow-steps)
5. [Project Structure](#project-structure)
6. [API Usage](#api-usage)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This project implements an **end-to-end data enrichment pipeline** for library book records:
- **Input**: Raw library dataset without book descriptions
- **Process**: Multi-source data enrichment using OpenLibrary and Google Books APIs
- **Output**: Enriched dataset with descriptions stored in SQLite database
- **Access**: FastAPI-based REST API for querying books

### Key Features
✅ Multi-source data enrichment  
✅ Fallback strategy for maximum data coverage  
✅ SQLite database storage  
✅ RESTful API with FastAPI  
✅ Support for Indian publications

---

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows/Linux/MacOS
- **RAM**: Minimum 4GB recommended
- **Storage**: ~500MB for data and dependencies

### Required Knowledge
- Basic Python programming
- Understanding of pandas DataFrames
- Basic SQL knowledge (optional)
- REST API concepts (optional)

---

## ⚙️ Setup Instructions

### Step 1: Clone/Download the Project
```bash
# If using Git
git clone <repository-url>

# Or download and extract the ZIP file
```

### Step 2: Navigate to Project Directory
```bash
cd Big-Data-Engineering-
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required Packages:**
- `requests` - For API calls
- `beautifulsoup4` - For web scraping
- `fastapi` - For REST API
- `pandas` - For data manipulation
- `uvicorn` - For running FastAPI server

### Step 4: Verify Installation
```bash
python -c "import requests, pandas, fastapi; print('All packages installed successfully!')"
```

---

## 🔄 Workflow Steps

### Phase 1: Data Preparation

#### Step 1.1: Load Raw Data
📁 **Location**: `Data-Building/load_data.ipynb`

**Purpose**: Load and explore the raw library dataset

**Actions**:
1. Open the notebook in Jupyter/VS Code
2. Run all cells sequentially
3. This will load `dau_library_data.csv` from `Data/raw_data/`
4. Verify the dataset has 10 columns (no description column initially)

**Expected Output**:
- DataFrame with library book information
- Sample rows displayed for verification

---

### Phase 2: Description Enrichment

#### Step 2.1: Fetch Descriptions from Multiple Sources
📁 **Location**: `Data-Building/fetch_description.ipynb`

**Purpose**: Enrich books with descriptions using OpenLibrary and Google Books APIs

**Data Sources Priority**:
1. **OpenLibrary API** (Primary, ISBN-based)
2. **Google Books HTML Scraping** (Fallback)
3. **Google Books API** (Final Fallback)

**Actions**:
1. Open `fetch_description.ipynb`
2. Run cells sequentially:
   - Cell 1: Import libraries
   - Cell 2: Load the raw dataset
   - Cell 3-5: Define API fetching functions
   - Cell 6-8: Implement fallback logic
   - Cell 9: Process all books (may take 30-60 minutes for large datasets)
   - Cell 10: Save enriched data

**Important Notes**:
- ⏱️ Processing time depends on dataset size (expect ~1-2 seconds per book)
- 🌐 Requires stable internet connection
- 🔄 Script includes retry logic for failed API calls
- 💾 Intermediate results are saved periodically

**Expected Output**:
- CSV file with added `description` column
- Coverage report showing success rate
- File saved to `Data/processed/dau_with_description.csv`

---

### Phase 3: Database Setup

#### Step 3.1: Create SQLite Database
📁 **Location**: `Database/SQLite3.py`

**Purpose**: Load enriched data into SQLite database for efficient querying

**Actions**:
```bash
cd Database
python SQLite3.py
```

**What it does**:
1. Reads the enriched CSV file from `Data/processed/dau_with_description.csv`
2. Creates a SQLite database (`db.sqlite3`)
3. Creates `books` table with proper schema
4. Inserts all book records with descriptions
5. Creates indexes for faster queries

**Database Schema**:
```sql
CREATE TABLE books (
    Acc_Date TEXT,
    Acc_No INTEGER PRIMARY KEY,
    Title TEXT,
    ISBN INTEGER,
    Author_Editor TEXT,
    Edition_Volume TEXT,
    Place_Publisher TEXT,
    Year INTEGER,
    Pages TEXT,
    Class_No TEXT,
    description TEXT
)
```

**Verification**:
```bash
# Check if database was created
ls -l db.sqlite3

# Or on Windows
dir db.sqlite3
```

---

### Phase 4: API Deployment

#### Step 4.1: Start the FastAPI Server
📁 **Location**: `API/book_api.py`

**Purpose**: Provide REST API access to the book database

**Actions**:
```bash
cd API
uvicorn book_api:app --reload
```

**Alternative (with custom port)**:
```bash
uvicorn book_api:app --reload --port 8080
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using statreload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Phase 5: Testing & Usage

#### Step 5.1: Test API Endpoints

**1. Root Endpoint (Health Check)**
```bash
# Browser
http://localhost:8000/

# cURL
curl http://localhost:8000/
```

**Expected Response**:
```json
{
    "message": "Book Library API is working"
}
```

**2. Get All Books (with limit)**
```bash
# Browser
http://localhost:8000/books?limit=10

# cURL
curl "http://localhost:8000/books?limit=10"
```

**Expected Response**:
```json
{
    "count": 10,
    "data": [
        {
            "Acc_No": 12345,
            "Title": "Sample Book Title",
            "Author_Editor": "John Doe",
            "ISBN": "9781234567890",
            "description": "This is a sample book description...",
            ...
        }
    ]
}
```

**3. Search by ISBN**
```bash
# Browser
http://localhost:8000/book?isbn=9781234567890

# cURL
curl "http://localhost:8000/book?isbn=9781234567890"
```

**4. Interactive API Documentation**
```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

---

## 📁 Project Structure

```
Big-Data-Engineering-/
│
├── API/                          # REST API Layer
│   ├── book_api.py              # FastAPI application
│   └── __pycache__/             # Python cache
│
├── Data/                         # Data Storage
│   ├── raw_data/                # Original datasets
│   │   └── dau_library_data.csv # Raw library data (no descriptions)
│   └── processed/               # Enriched datasets
│       └── dau_with_description.csv # Final enriched data
│
├── Data-Building/               # Data Processing Scripts
│   ├── load_data.ipynb         # Step 1: Load raw data
│   └── fetch_description.ipynb # Step 2: Fetch descriptions
│
├── Database/                    # Database Layer
│   ├── db.sqlite3              # SQLite database file
│   └── SQLite3.py              # Database creation script
│
├── logs/                        # Project Documentation
│   └── prompt.md               # Project prompts/notes
│
├── README.md                    # Project overview
├── requirements.txt             # Python dependencies
└── workflow.md                  # This file
```

---

## 🔌 API Usage

### Available Endpoints

#### 1. **GET /** - Health Check
```http
GET http://localhost:8000/
```

#### 2. **GET /books** - Get Multiple Books
```http
GET http://localhost:8000/books?limit=100
```

**Query Parameters**:
- `limit` (optional): Number of books to fetch (default: 1000, max: 5000)

**Response**:
```json
{
    "count": 100,
    "data": [...]
}
```

#### 3. **GET /book** - Get Book by ISBN
```http
GET http://localhost:8000/book?isbn=9781234567890
```

**Query Parameters**:
- `isbn` (required): ISBN number of the book

**Response**:
```json
{
    "Acc_No": 12345,
    "Title": "Book Title",
    "Author_Editor": "Author Name",
    "ISBN": "9781234567890",
    "description": "Book description...",
    ...
}
```

### Using the API in Your Application

**Python Example**:
```python
import requests

# Get multiple books
response = requests.get("http://localhost:8000/books?limit=50")
books = response.json()
print(f"Found {books['count']} books")

# Search by ISBN
isbn = "9781234567890"
response = requests.get(f"http://localhost:8000/book?isbn={isbn}")
book = response.json()
print(f"Title: {book['Title']}")
```

**JavaScript Example**:
```javascript
// Fetch multiple books
fetch('http://localhost:8000/books?limit=50')
    .then(response => response.json())
    .then(data => console.log(`Found ${data.count} books`));

// Search by ISBN
fetch('http://localhost:8000/book?isbn=9781234567890')
    .then(response => response.json())
    .then(book => console.log(`Title: ${book.Title}`));
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Import Errors
**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
# Or install individually
pip install fastapi uvicorn pandas requests beautifulsoup4
```

---

#### Issue 2: Database Path Issues
**Error**: `sqlite3.OperationalError: unable to open database file`

**Solution**:
1. Check if the database file exists:
   ```bash
   cd Database
   ls db.sqlite3
   ```
2. Update the `DB_PATH` in `API/book_api.py` to use relative or correct absolute path
3. Re-run `SQLite3.py` to recreate the database

---

#### Issue 3: API Connection Timeout
**Error**: API calls in `fetch_description.ipynb` timing out

**Solution**:
1. Check internet connection
2. Increase timeout in the code:
   ```python
   response = requests.get(url, timeout=30)  # Increase from default
   ```
3. Add retry logic with exponential backoff

---

#### Issue 4: Port Already in Use
**Error**: `ERROR: [Errno 48] Address already in use`

**Solution**:
```bash
# Use a different port
uvicorn book_api:app --reload --port 8080

# Or kill the process using the port (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

#### Issue 5: Empty Descriptions
**Problem**: Many books have null/empty descriptions after fetching

**Solution**:
1. This is expected for some books (especially Indian publications)
2. Check the fallback logic is working:
   - OpenLibrary → Google Books HTML → Google Books API
3. Manually verify a few ISBNs on OpenLibrary/Google Books websites
4. Consider adding more data sources in the fallback chain

---

#### Issue 6: CSV Encoding Issues
**Error**: `UnicodeDecodeError` when reading CSV

**Solution**:
```python
# Try different encodings
df = pd.read_csv("file.csv", encoding='latin1')
# Or
df = pd.read_csv("file.csv", encoding='utf-8')
# Or
df = pd.read_csv("file.csv", encoding='cp1252')
```

---

## 📊 Expected Results

After completing the entire workflow:

### Data Statistics (Sample)
- **Total Books**: ~5,000-10,000 (depends on your dataset)
- **Books with Descriptions**: ~60-80% (varies based on data sources)
- **Processing Time**: 1-2 hours (for 10,000 books)
- **Database Size**: ~50-100 MB
- **API Response Time**: <100ms per query

### Quality Metrics
- **OpenLibrary Coverage**: ~30-40%
- **Google Books Coverage**: ~40-50%
- **Overall Success Rate**: ~70-85%

---

## 🚀 Next Steps

After completing this workflow, you can:

1. **Enhance the API**:
   - Add search by title/author
   - Implement pagination
   - Add filtering and sorting
   - Create advanced query endpoints

2. **Improve Data Quality**:
   - Add more data sources (Amazon, WorldCat, etc.)
   - Implement data validation
   - Add description quality scoring
   - Clean and normalize existing descriptions

3. **Deploy to Production**:
   - Use PostgreSQL instead of SQLite
   - Deploy API to cloud (AWS, GCP, Azure)
   - Add authentication and rate limiting
   - Implement caching (Redis)

4. **Create Frontend**:
   - Build a web interface
   - Create search functionality
   - Add data visualization
   - Implement book recommendation system

---

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [OpenLibrary API](https://openlibrary.org/developers/api)
- [Google Books API](https://developers.google.com/books)

### Helpful Commands
```bash
# Check Python version
python --version

# List installed packages
pip list

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Export current environment
pip freeze > requirements.txt

# Check API is running
curl http://localhost:8000/
```

---

## 👥 Support

If you encounter issues not covered in this workflow:
1. Check the README.md for additional context
2. Review the code comments in Python files and notebooks
3. Verify all prerequisites are met
4. Check the logs folder for any project-specific notes

---

## 📝 Notes

- **Database Path**: Update absolute paths in `SQLite3.py` and `book_api.py` based on your system
- **API Rate Limits**: Be mindful of rate limits when fetching from external APIs
- **Data Privacy**: Ensure you have rights to use and distribute the library data
- **Performance**: For large datasets (>50k books), consider batch processing and caching

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Project Type**: Big Data Engineering - Data Enrichment Pipeline

---

*Happy Data Engineering! 🎉*
