import nltk
import os

def download_if_missing(package):
    try:
        nltk.data.find(package)
        print(f"✅ {package} already exists.")
    except LookupError:
        print(f"⏳ Downloading {package}...")
        nltk.download(package)

if __name__ == "__main__":
    packages = ["punkt", "stopwords", "wordnet", "omw-1.4"]
    for p in packages:
        download_if_missing(p)
    print("✨ NLTK check complete.")
