# =========================
# book_recommender.py
# =========================

import pandas as pd
import numpy as np
import torch
import re
import gc

from gensim.models import Word2Vec
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# -------------------------
# DEVICE SETUP
# -------------------------
def get_device():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
    print(f"Using device: {device}")
    return device


# -------------------------
# NLTK SETUP
# -------------------------
def setup_nltk():
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")
    nltk.download("omw-1.4")


STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


# -------------------------
# TEXT CLEANING
# -------------------------
def clean_basic(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.strip()


def clean_desc_nltk(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    tokens = word_tokenize(text)
    tokens = [
        LEMMATIZER.lemmatize(word)
        for word in tokens
        if word not in STOP_WORDS and len(word) > 2
    ]

    return " ".join(tokens)


# -------------------------
# DATA LOADING
# -------------------------
def load_dataset(csv_path):
    df = pd.read_csv(csv_path)

    df["Title"] = df["Title"].fillna("")
    df["Author_Editor"] = df["Author_Editor"].fillna("")
    df["description"] = df["description"].fillna("")

    df["clean_title"] = df["Title"].apply(clean_basic)
    df["clean_author"] = df["Author_Editor"].apply(clean_basic)
    df["clean_desc"] = df["description"].apply(clean_desc_nltk)

    return df


# -------------------------
# WORD2VEC
# -------------------------
def train_word2vec(df):
    title_sentences = [row.split() for row in df["clean_title"]]
    author_sentences = [row.split() for row in df["clean_author"]]

    print("Training Title Word2Vec...")
    w2v_title = Word2Vec(
        sentences=title_sentences,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4
    )

    print("Training Author Word2Vec...")
    w2v_author = Word2Vec(
        sentences=author_sentences,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4
    )

    return w2v_title, w2v_author


def sentence_vector(sentence, model):
    words = sentence.split()
    vectors = [model.wv[w] for w in words if w in model.wv]
    if not vectors:
        return np.zeros(model.vector_size)
    return np.mean(vectors, axis=0)


# -------------------------
# SENTENCE TRANSFORMER
# -------------------------
def load_sentence_transformer(device):
    return SentenceTransformer("all-MiniLM-L6-v2", device=device.type)


def generate_description_embeddings(df, model):
    print("Generating description embeddings...")
    embeddings = model.encode(
        df["description"].tolist(),
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings


# -------------------------
# QUERY PARSING
# -------------------------
def parse_query(query):
    query = query.lower()
    k = 5

    if re.search(r"\b(one|1|single)\b", query):
        k = 1
    elif re.search(r"\b(two|2)\b", query):
        k = 2
    elif re.search(r"\b(three|3)\b", query):
        k = 3
    elif re.search(r"\b(top|best)\s+(\d+)\b", query):
        k = int(re.search(r"\b(top|best)\s+(\d+)\b", query).group(2))

    clean_query = re.sub(
        r"\b(send|give|show|recommend|find|get|i want|me|book|books|which|is|are|to|about)\b",
        "",
        query
    )
    clean_query = re.sub(r"\s+", " ", clean_query).strip()

    return clean_query if len(clean_query) > 2 else query, k


# -------------------------
# RECOMMENDER CLASS
# -------------------------
class BookRecommender:
    def __init__(self, df, st_model):
        self.df = df
        self.st_model = st_model
        self.description_matrix = np.stack(df["description_vec"].values)

    def recommend(self, user_query):
        topic, k = parse_query(user_query)
        print(f"Searching: '{topic}' | Top-{k}")

        query_vec = self.st_model.encode([topic])
        similarities = cosine_similarity(query_vec, self.description_matrix)

        top_indices = similarities[0].argsort()[-k:][::-1]

        return self.df.iloc[top_indices][
            ["Title", "Author_Editor", "description", "image_url"]
        ]


# -------------------------
# INITIALIZATION (FOR FASTAPI)
# -------------------------
def initialize_recommender(csv_path):
    setup_nltk()
    device = get_device()

    df = load_dataset(csv_path)

    st_model = load_sentence_transformer(device)
    df["description_vec"] = list(
        generate_description_embeddings(df, st_model)
    )

    recommender = BookRecommender(df, st_model)
    return recommender


# -------------------------
# LOCAL TEST
# -------------------------
if __name__ == "__main__":
    recommender = initialize_recommender(
        "D:/1Project demo/dau_with_description.csv"
    )

    query = "send me one book which is highly correlated to data science"
    result = recommender.recommend(query)
    print(result)
