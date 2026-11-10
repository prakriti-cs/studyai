import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity


def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def remove_stop_words(text):
    return " ".join(w for w in text.split() if w not in ENGLISH_STOP_WORDS)


def get_similarity_scores(documents, query):
    """TF-IDF + cosine similarity, one score per document.

    It compares pieces of words (3 to 5 letters) instead of whole words,
    so spelling mistakes like "serch" still match "search".
    """
    documents = [remove_stop_words(preprocess(d)) for d in documents]
    query = remove_stop_words(preprocess(query))

    if not query:
        return np.zeros(len(documents))

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
    matrix = vectorizer.fit_transform(documents + [query])
    return cosine_similarity(matrix[-1], matrix[:-1])[0]
