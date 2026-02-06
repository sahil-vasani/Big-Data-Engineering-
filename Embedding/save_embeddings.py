import numpy as np
import pickle
from book_recommender import (
    initialize_recommender
)

# Initialize once
recommender = initialize_recommender(
    "D:/COLLAGE/DAIICT/2 - SEM/BDE/Project/Big-Data-Engineering-/Data/processed/dau_with_description.csv"
)

# Save embeddings
np.save("book_embeddings.npy", recommender.description_matrix)

# Save metadata (no vectors)
with open("books_metadata.pkl", "wb") as f:
    pickle.dump(recommender.df, f)

print("✅ Embeddings & metadata saved")
