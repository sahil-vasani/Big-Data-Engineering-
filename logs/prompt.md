# 📄 Prompt Documentation – Book Description Enrichment Pipeline

This document contains the prompts and answers used to explain the data enrichment strategy applied in the Book Description Enrichment Pipeline project.

---

## 🟢 Prompt 1  
### From which sources did you fetch book descriptions if the library data (`library.csv`) already exists?

**Answer:**
- The base library dataset already contained book metadata but no descriptions  
- Descriptions were fetched from **OpenLibrary API** using ISBN  
- **Google Books** was used as a secondary source  
  - HTML scraping using ISBN  
  - Google Books API as fallback  
- For remaining missing cases, descriptions were fetched using **Title + Author** search on Google Books  

---

## 🟢 Prompt 2  
### How can book descriptions be scraped using OpenLibrary?

**Answer:**

There are **two ways** to fetch book descriptions from OpenLibrary:

---

### 1️⃣ Using OpenLibrary API (Preferred Method)

- Use the OpenLibrary Books API with ISBN as input  
- Endpoint example:  
/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data

- Extract the `description` field from the JSON response  
- Fast and reliable  
- Structured data (no HTML parsing required)  
- Suitable for large-scale processing  

**Limitations:**
- Many Indian publications return `"Not Found"`  
- Some books do not have descriptions available via API  

---

### 2️⃣ Using HTML Scraping (BeautifulSoup)

- Access the OpenLibrary book detail page using ISBN or work ID  
- Parse HTML content using **BeautifulSoup**  
- Extract description text from relevant HTML tags  
- Used when API does not return a description  

**Benefits of HTML Scraping:**
- Allows cross-verification with original webpage content  
- Some descriptions exist on the webpage but not in the API  
- Useful as a fallback strategy  

---

## 🟢 Prompt 3  
### Can we first scrape from Google Books and then OpenLibrary and cross-verify both?

**Answer:**

Yes, the data enrichment process can be designed using a **cross-verification strategy** as follows:

---

### 1️⃣ Primary Source – Google Books

- Fetch or scrape book descriptions from **Google Books**  
- Methods used:
- HTML scraping using ISBN  
- API fallback when available  
- Reason:
- Better coverage for Indian and international publications  
- Richer and more detailed descriptions  

---

### 2️⃣ Secondary Source – OpenLibrary

- Fetch descriptions using **OpenLibrary API** or HTML pages  
- Used as a **verification and fallback source**  
- Helps validate the authenticity of descriptions  

---

### 3️⃣ Cross-Verification Logic

- If description is found in **both sources**:
- Compare length and content similarity  
- Prefer the more detailed or non-null description  
- If description exists in **only one source**:
- Accept the available description  
- If descriptions mismatch:
- Give priority to Google Books (higher coverage)  
- Use OpenLibrary for validation  

---

## 🟢 Prompt 4  
### What do you do if book descriptions are still not found after Google Books and OpenLibrary?

**Answer:**

---

### 🔁 Final Fallback – Title + Author Based Fetch

- Identify records where description is still `"Not Found"` or null  
- Ignore ISBN for these records  
- Use **Title + Author** as the search query  

---

### 🔍 Search Strategy

- Clean title and author text:
- Convert to lowercase  
- Remove punctuation and extra spaces  
- Send query to **Google Books search endpoint**  
- Fetch the most relevant matching result  

---

### 📝 Description Extraction

- Extract description from:
- Google Books API response, or  
- Google Books HTML page (if API fails)  
- Validate that the returned book matches the given title and author  

---

### ✅ Why Title + Author Works

- Many books have:
- Missing ISBN  
- Incorrect ISBN  
- Local or Indian editions without ISBN  
- Title + Author provides semantic matching  
- Increases description recovery rate  

---

## 🟢 Prompt 5
### which model is used for embedding like pretrained model or trasnformer which give best result ?
For building a semantic search or book recommendation project, you should use a pretrained transformer embedding model, because transformer models provide the best semantic understanding of text.

The recommended model is:

sentence-transformers/all-MiniLM-L6-v2

This is a pretrained transformer model that converts text into dense vectors (embeddings) which capture the meaning and context of the sentence. It provides excellent accuracy, very fast performance, and low memory usage, making it ideal for real-time applications.

Transformer-based pretrained models give much better results than traditional methods like TF-IDF or Bag-of-Words because they understand semantic similarity, not just keyword matching.

If higher accuracy is required and memory is not a limitation, you can also use sentence-transformers/all-mpnet-base-v2, which provides even better embedding quality but is slower and larger.

For most projects, all-MiniLM-L6-v2 is the best starting choice.

## 🟢 Prompt 6
### how to take pretrained model ? and which model is usefull for my book recommendation system ?

To use a pretrained embedding model in your book recommendation system, you can download and load it directly from Hugging Face using the Sentence Transformers library. These models are already trained and ready to use, so you do not need to train anything from scratch.

  #### code Reference

## 🟢 Prompt 7
### How do I apply a pretrained embedding model to my dataset and build a book recommendation system?

After loading a pretrained embedding model, the process involves converting your dataset into embeddings, storing them, and using similarity search to generate recommendations. This is typically done in three main stages: embedding generation, storage, and retrieval.

Step 1: Define the project objective
Clearly define the goal of your system. In this case, the objective is to recommend books based on the semantic meaning of user queries using a pretrained transformer embedding model.

Step 2: Collect and prepare the dataset
Gather your book dataset containing important fields such as:
Acc. No.
Acc. Date
Title
ISBN
Author/Editor
Ed./Vol.
Place & Publisher
Year
Page(s)
Class No./Book No.
Book description 
The description field is critical because embeddings will be generated from this text.

Step 3: Clean and preprocess the data
Improve data quality by performing:
Removing duplicate records
Handling missing descriptions
Normalizing text (removing unwanted symbols, formatting issues)
Ensuring consistent and meaningful descriptions
Clean data improves embedding quality and recommendation accuracy.

Step 4: Select and load a pretrained embedding model
Choose a pretrained transformer model suitable for semantic similarity tasks.
Recommended model:
sentence-transformers/all-MiniLM-L6-v2
This model converts text into numerical vectors that capture semantic meaning.
Step 5: Generate embeddings for your dataset (offline process)
Convert each book description into an embedding vector using the pretrained model.
Each book will now have a numeric representation that reflects its meaning.
This step is done once and stored for future use.

Step 6: Store embeddings and metadata
Save the generated embeddings and book metadata in a storage system such as:
NumPy file (.npy) for embeddings
SQLite database, CSV, or JSON for metadata
This allows fast retrieval without recomputing embeddings.

Step 7: Build the semantic search system
When a user enters a query:
Convert the user query into an embedding using the same pretrained model
Compare the query embedding with stored book embeddings
Calculate similarity scores
Identify the most similar books

Step 8: Retrieve and display recommendations
Select the top matching books based on similarity score and return them to the user through your application interface.

Step 9: Deploy the system
Deploy the system using a backend framework such as FastAPI and host it on a cloud platform. Ensure embeddings and models are accessible during runtime

#### code reference 

## 🟢 Prompt 8
### Which platforms provide free hosting for deploying a  model and recommendation system?
Several cloud platforms offer free tiers that allow you to deploy machine learning models and AI applications. The best platform depends on your project size, architecture, and deployment requirements.

1. Hugging Face (Best for ML models)
Recommended for: Machine learning models, NLP systems, and semantic search applications
Free tier features:
Free model hosting
Free deployment using Hugging Face Spaces
Built-in support for transformer models
Automatic scaling for small workloads
Why it is useful:
Hugging Face is specifically designed for ML deployment and provides native support for pretrained models, making deployment simple and efficient.

2. Railway (Best for full backend deployment)
Recommended for: FastAPI, backend APIs, and full-stack ML systems
Free tier features:
Free monthly usage credits
Easy GitHub integration
Supports Docker deployment
Automatic HTTPS and public URL

Why it is useful:
Railway is ideal for deploying complete AI applications including backend, API, and database.

3. Render (Best Railway alternative)
Recommended for: Backend APIs and ML model serving
Free tier features:
Free web service hosting
Automatic deployment from GitHub
Supports Python, FastAPI, and Docker

Why it is useful:
Render provides stable free hosting and is suitable for production-ready ML APIs.

4. Vercel (Best for frontend + lightweight backend)
Recommended for: Frontend deployment with lightweight ML APIs
Free tier features:
Free frontend hosting
Serverless functions support
Fast global CDN
Limitation:
Not ideal for heavy ML models.

## 🟢 Prompt 9
### How can I generate a Hugging Face access token and securely deploy my ML model assets on Hugging Face while deploying the API on Railway?
To deploy your machine learning system using Hugging Face (for model and embeddings hosting) and Railway (for backend API hosting), you need to generate a Hugging Face access token and configure it properly in Railway. Follow these professional deployment steps:

Part 1: Create a Hugging Face Account
Go to Hugging Face
Click Sign Up
Create your account using email or GitHub
Verify your email and log in
This account will host your model files and embeddings.

Part 2: Create a Model Repository on Hugging Face
Click your Profile icon (top-right corner)
Select Your repositories
Click New repository

Choose:
Repository name: book-recommender-assets
Visibility: Public (recommended) or Private

Repository type: Model
Click Create repository
This repository will store files like:
Ex.embeddings.npy
books.db

model files

Part 3: Upload your model and embedding files
Open your repository
Click Upload files
Upload:
book_embeddings.npy
books.db

any required model assets
Click Commit changes
Your assets are now securely hosted.

Part 4: Generate a Hugging Face Access Token
This token allows your Railway backend to securely download model files.
Steps:
Click your Profile icon
Go to Settings
Click Access Tokens
Click New token

Enter:
Name: railway-access-token
Role: Read
Click Generate token
Copy the token

Example token format:
hf_xxxxxxxxxxxxxxxxxxxxx
Keep this token secure.

Part 5: Prepare your project for Railway deployment
Ensure your project includes:
FastAPI backend
requirements.txt
Dockerfile (optional but recommended)
Code that downloads assets from Hugging Face
Push your project to GitHub.

Part 6: Create Railway account and deploy backend
Go to Railway
Sign up using GitHub
Click New Project
Select Deploy from GitHub Repo
Choose your project repository

Railway will start deployment.

Part 7: Add Hugging Face token to Railway environment variables
This is the most important step.
Open your Railway project

Click Variables tab
Add new variable:

Key: HF_TOKEN
Value: hf_xxxxxxxxxxxxxxxxx

Add another variable:

Key: HF_HOME
Value: /app/.cache/huggingface

This allows Railway to securely download model assets.

Part 8: Configure start command in Railway
Go to Settings → Start Command
Enter:
uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}

Part 9: Deploy and verify deployment
Railway will now:
Build your application
Download model assets from Hugging Face
Start FastAPI server
Provide a public deployment URL
Example:
https://your-app-name.up.railway.app

