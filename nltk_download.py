import nltk

def download_nltk_data():
    print("Downloading NLTK data...")
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("omw-1.4")
    print("NLTK data downloaded successfully.")

if __name__ == "__main__":
    download_nltk_data()
