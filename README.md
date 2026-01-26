# 📚 Book Description Enrichment Pipeline
### Big Data Engineering Mini Project

A comprehensive data engineering pipeline to enrich library book records with missing descriptions using multiple public data sources, followed by structured storage in SQLite and API-based access via FastAPI.

---

## 📑 Table of Contents
- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Data Sources](#-data-sources)
- [Dataset Evolution](#-dataset-evolution)
- [Final Data Schema](#-final-data-schema)
- [Database Design](#-database-design)
- [API Endpoints](#-api-endpoints-fastapi)
- [Technologies Used](#-technologies-used) 
- [How to Run](#-how-to-run)
- [Key Learnings](#-key-learnings)

---

## 📌 Overview
This project implements an **end-to-end data enrichment pipeline** that:

- Starts from a raw library dataset with **no book descriptions**
- Collects missing descriptions from **multiple external sources**
- Applies **multi-stage fallback logic** to maximize coverage
- Cleans and merges data into a **final unified dataset**
- Stores enriched data in **SQLite**
- Serves data using **FastAPI REST endpoints**

This project reflects **real-world data engineering challenges**, especially for **Indian publications**, where book descriptions are often unavailable from a single source.

---

## ❓ Problem Statement
The original dataset (`dau_library.csv`) did not contain a book description column. Additionally:

- OpenLibrary provides **limited coverage** for Indian books
- ISBN-based lookups frequently fail
- A **single data source was insufficient**

To solve this, a **multi-source enrichment and fallback strategy** was designed.

---

## 🧩 Data Sources
- **Local Library Dataset (CSV)**
- **OpenLibrary API** (ISBN-based)
- **Google Books**
  - HTML scraping
  - API fallback
  - Title + Author search

---

## 🗂 Dataset Evolution

### 1️⃣ Base Dataset (No Descriptions)
**File:** `dau_library.csv`

Contains:
- Accession Date
- Accession Number
- Title
- ISBN
- Author / Editor
- Edition / Volume
- Publisher
- Year
- Pages
- Classification Number

❌ No description column

---

### 2️⃣ ISBN-Based Description Fetch (OpenLibrary)
**File:** `OpenLibrary_5000.csv`

- Selected first **5,000 records**
- Used ISBN to fetch descriptions from OpenLibrary API

**Result:**
- Partial success
- Many `"Not Found"` values

---

### 3️⃣ Google Books HTML Scraping (Large Scale)
**File:** `HTML_tag_through_All_36000.csv`

- Scraped descriptions using ISBN
- Parsed HTML tags from Google Books
- Covered ~36,000 records

**Result:**
- Higher coverage than OpenLibrary
- Still some missing descriptions

---

### 4️⃣ First Merge (Google Books + OpenLibrary)
**File:** `Final_Merged_Descriptions.csv`

**Merge Logic:**
- Primary source → Google Books
- Fallback source → OpenLibrary
- If Google Books description is missing:
  - Fill using OpenLibrary description

**Result:**
- Significant reduction in missing descriptions

---

### 5️⃣ Title + Author Based Fetch (Final Fallback)
**File:** `Final_GoogleBooks_Descriptions.csv`

- Applied to remaining `"Not Found"` rows
- Used **Title + Author** based search
- Cleaned text (lowercase, punctuation removal)

**Result:**
- Many additional descriptions recovered

---

### 6️⃣ Final Clean Dataset
**File:** `dau_with_description.csv`

Merged:
- `Final_Merged_Descriptions.csv`
- `Final_GoogleBooks_Descriptions.csv`

✅ Used for SQLite database insertion

---

## 🧾 Final Data Schema

| Column Name | Description |
|------------|------------|
| acc_no | Accession number |
| title | Book title |
| isbn | ISBN number |
| author_editor | Author / Editor |
| publisher | Publisher details |
| year | Publication year |
| pages | Number of pages |
| class_no | Classification number |
| description | Enriched book description |

---

## 🗄 Database Design
**Database:** `library.db`

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acc_no TEXT,
    title TEXT,
    isbn TEXT,
    author_editor TEXT,
    publisher TEXT,
    year INTEGER,
    pages INTEGER,
    class_no TEXT,
    description TEXT
);

---

## 🚀 API Endpoints (FastAPI)

The project exposes RESTful endpoints using **FastAPI** to access enriched book data stored in SQLite.

| Method | Endpoint | Description |
|------|---------|------------|
| GET | `/books` | Fetch all books |
| GET | `/books/{id}` | Fetch a single book by ID |
| GET | `/search` | Search books by title, author, or ISBN |

### 🔍 Example Request
```http
GET /search?title=data```

---

## 🛠 Technologies Used
- Python 3.9+
- Pandas
- Requests
- BeautifulSoup
- SQLite3
- FastAPI
- Uvicorn
- Jupyter Notebook

---

## ▶️ How to Run

### 1️⃣ Install Dependencies
Make sure Python 3.9+ is installed, then run:
```bash
pip install -r requirements.txt

2️⃣ Start FastAPI Server
uvicorn main:app --reload

3️⃣ Open API Documentation
Open your browser and visit:
http://127.0.0.1:8000/docs

 


