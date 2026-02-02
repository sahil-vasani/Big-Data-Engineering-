import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote_plus
 
INPUT_CSV = "dau_library_data.csv"
FINAL_OUTPUT = "dau_with_description.csv"

MISSING_VALUES = ["Not Found", "ISBN Not Matched", "Description Not Available"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Sahil-BookBot/1.0)"
}
 

def clean_isbn(isbn):
    return re.sub(r"[^0-9Xx]", "", str(isbn))

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text
 

def load_library_data():
    columns = [
        "Acc_Date", "Acc_No", "Title", "ISBN", "Author_Editor",
        "Edition_Volume", "Place_Publisher", "Year", "Pages", "Class_No"
    ]

    df = pd.read_csv(
        INPUT_CSV,
        usecols=range(len(columns)),
        names=columns,
        header=0,
        encoding="latin1"
    )

    df = df.drop_duplicates(subset=[
        "Title", "ISBN", "Author_Editor",
        "Edition_Volume", "Place_Publisher",
        "Year", "Pages", "Class_No"
    ])

    df["description"] = "Not Found"
    return df
 

def fetch_openlibrary_descriptions(df, limit=5000):
    df = df.copy()
    for i, row in df.iloc[:limit].iterrows():
        isbn = clean_isbn(row["ISBN"])
        desc = "ISBN Not Matched"

        if isbn:
            try:
                url = f"https://openlibrary.org/isbn/{isbn}"
                r = requests.get(url, headers=HEADERS, timeout=10)

                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")
                    p = soup.select_one("div.book-description div.read-more__content p")
                    desc = p.get_text(strip=True) if p else "Description Not Available"
            except:
                pass

        df.at[i, "description"] = desc
        time.sleep(1)

    return df
 

def fetch_google_html_descriptions(df):
    df = df.copy()

    for i, row in df.iterrows():
        if df.at[i, "description"] not in MISSING_VALUES:
            continue

        isbn = clean_isbn(row["ISBN"])
        desc = "Not Found"

        if isbn:
            try:
                url = f"https://books.google.com/books?vid=ISBN{isbn}"
                r = requests.get(url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                div = soup.find("div", id="synopsis")
                if div:
                    desc = div.get_text(separator=" ", strip=True)
            except:
                pass

        df.at[i, "description"] = desc
        time.sleep(0.2)

    return df
 

def google_books_api_search(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
    try:
        res = requests.get(url, timeout=10).json()
        items = res.get("items")
        if not items:
            return None
        return items[0].get("volumeInfo", {}).get("description")
    except:
        return None

def fetch_google_api_fallback(df):
    df = df.copy()

    df["clean_title"] = df["Title"].apply(clean_text)
    df["clean_author"] = df["Author_Editor"].apply(clean_text)

    for i, row in df.iterrows():
        if row["description"] not in MISSING_VALUES:
            continue

        queries = [
            f"intitle:{row['clean_title']}+inauthor:{row['clean_author']}",
            f"intitle:{row['clean_title']}"
        ]

        for q in queries:
            desc = google_books_api_search(quote_plus(q))
            if desc and len(desc) > 50:
                df.at[i, "description"] = desc
                break

        time.sleep(0.2)

    return df.drop(columns=["clean_title", "clean_author"])
 
def run_pipeline():
    print("🔹 Loading base library data...")
    df = load_library_data()

    print("🔹 Fetching OpenLibrary descriptions...")
    df = fetch_openlibrary_descriptions(df)

    print("🔹 Fetching Google Books HTML descriptions...")
    df = fetch_google_html_descriptions(df)

    print("🔹 Fetching Google Books API fallback descriptions...")
    df = fetch_google_api_fallback(df)

    print("🔹 Saving FINAL output...")
    df.to_csv(FINAL_OUTPUT, index=False)

    print(f"\n✅ DONE Final file created: {FINAL_OUTPUT}")
 

if __name__ == "__main__":
    run_pipeline()
