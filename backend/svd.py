from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import numpy as np

def svd(actors_df, query):

    vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7,
                                min_df = 75)
    td_matrix = vectorizer.fit_transform([(x[1] + x[2]) for x in actors_df])
    # do SVD with a very large k (we usually use 100), just for the sake of getting many sorted singular values (aka importances)
    u, s, v_trans = svds(td_matrix, k=100)
    docs_compressed, s, words_compressed = svds(td_matrix, k=40)
    words_compressed = words_compressed.transpose()

    docs_compressed_normed = normalize(docs_compressed)

    query_tfidf = vectorizer.transform([query]).toarray()
    query_vec = normalize(np.dot(query_tfidf, words_compressed)).squeeze()
    sims = docs_compressed_normed.dot(query_vec)
    asort = np.argsort(-sims)[:25+1] #number closest matches
    return [(i, actors_df[i][0],sims[i]) for i in asort[1:]] #num in db, name, sim score



