# Big-Data-Engineering
📚 Book Description Enrichment Pipeline

Big Data Engineering Mini Project

📌 Project Overview

This project focuses on enriching a library book dataset with missing descriptions by collecting data from multiple public sources, cleaning it, storing it in a relational database, and exposing it through a FastAPI service.

The main challenge was that many books (especially Indian publications) did not have descriptions available in a single source. To solve this, a multi-stage data collection and merging strategy was used.
🧩 Data Sources Used

  * Local CSV (Library Data)

  * OpenLibrary API

  * Google Books (HTML scraping + API fallback)

🗂 Dataset Evolution (Step-by-Step)
1️⃣ Base Dataset (No Descriptions) 
File: dau_library.csv 
This is the original library dataset 
Contains metadata such as: 
Acc.
 Date,
 Acc. No.,
 Title,ISBN,Author/Editor,Ed./Vol.,Place & Publisher,Year,Page(s),Class No./Book No. 
❌ No description column

2️⃣ Description Fetch Using ISBN (OpenLibrary) 
File: OpenLibrary_5000.csv 
Selected first 5,000 rows from dau_library.csv 
Used ISBN to fetch descriptions from OpenLibrary API 
Result: 
Many descriptions fetched 
❌ Many "Not Found" values (OpenLibrary lacks Indian books)


3️⃣ Google Books HTML Scraping (Large-Scale) 
File: HTML_tag_through_All_36000.csv 
Used Google Books as a second source 
Scraped descriptions using: 
ISBN 
HTML parsing (tags) 
Covered ~36,000 books 
Result: 
More coverage than OpenLibrary 
Still some missing descriptions

4️⃣ First Merge (OpenLibrary + Google Books)

File: Final_Merged_Descriptions.csv 
Logic: 
Primary source → Google Books (HTML_tag_through_All_36000.csv) 
Fallback source → OpenLibrary (OpenLibrary_5000.csv) 
If Google Books description was null or not found: 
Filled it using OpenLibrary description (if available) 
Result: 
Significant reduction in missing descriptions

5️⃣ Title + Author Based Fetch (Final Fallback) 
File: Final_GoogleBooks_Descriptions (1).csv 
Still some rows had "Not Found" descriptions 
These books did not work well with ISBN 
New strategy: 
Fetch description using Title + Author from Google Books 
Result: 
Many additional descriptions recovered

6️⃣ Final Clean Dataset 
File: target_updated.csv 
Merged: 
Final_Merged_Descriptions.csv 
Final_GoogleBooks_Descriptions (1).csv  

✅ This file is used for database insertion