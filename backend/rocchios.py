import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_directory, 'data/final_celeb_info.csv')

# Read the CSV file into a DataFrame
celeb_df = pd.read_csv(csv_file_path)

def map_names_to_professions(names, celeb_df):
    professions = []
    for name in names:
        profession = celeb_df.loc[celeb_df['Celebrity Name'] == name, 'profession'].values
        if profession.size > 0:
            professions.append(profession[0])
    return professions

def map_names_to_traits(names, celeb_df):
    character_traits = []
    for name in names:
        character_trait = celeb_df.loc[celeb_df['Celebrity Name'] == name, 'Character Traits'].values
        if character_trait.size > 0:
            character_traits.append(character_trait[0])
    return character_traits

def extract_keywords_from_updated_vector(updated_query_vec, vectorizer, top_n=5):
    feature_array = np.array(vectorizer.get_feature_names_out())
    sorted_indices = np.argsort(updated_query_vec.flatten())[::-1]
    top_indices = sorted_indices[:top_n]
    top_keywords = feature_array[top_indices]
    return top_keywords.tolist()

def update_query_vector(query_profession, liked_names, disliked_names, celeb_df):
    liked_professions = map_names_to_professions(liked_names, celeb_df)
    disliked_professions = map_names_to_professions(disliked_names, celeb_df)

    corpus = [query_profession] + liked_professions + disliked_professions
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus).toarray()

    original_query_vec = X[0]

    liked_vec, disliked_vec = np.zeros_like(original_query_vec), np.zeros_like(original_query_vec)
    if liked_professions:
        liked_vec = np.mean(X[1:len(liked_professions)+1], axis=0)
    if disliked_professions:
        start_idx = 1 + len(liked_professions)
        disliked_vec = np.mean(X[start_idx:start_idx+len(disliked_professions)], axis=0)

    alpha, beta, gamma = 1, 0.75, 0.15
    updated_query_vec = alpha * original_query_vec + beta * liked_vec - gamma * disliked_vec

    top_keywords = extract_keywords_from_updated_vector(updated_query_vec, vectorizer)

    return ' '.join(top_keywords)

def update_query2_vector(query_traits, liked_names, disliked_names, celeb_df):
    # Second rocchio update function that uses character traits instead of professions
    liked_character_traits = map_names_to_traits(liked_names, celeb_df)
    disliked_character_traits = map_names_to_traits(disliked_names, celeb_df)

    corpus = [query_traits] + liked_character_traits + disliked_character_traits
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus).toarray()

    original_query_vec = X[0]

    liked_vec, disliked_vec = np.zeros_like(original_query_vec), np.zeros_like(original_query_vec)
    if liked_character_traits:
        liked_vec = np.mean(X[1:len(liked_character_traits)+1], axis=0)
    if disliked_character_traits:
        start_idx = 1 + len(liked_character_traits)
        disliked_vec = np.mean(X[start_idx:start_idx+len(disliked_character_traits)], axis=0)

    alpha, beta, gamma = 1, 0.75, 0.15
    updated_query_vec = alpha * original_query_vec + beta * liked_vec - gamma * disliked_vec

    top_keywords = extract_keywords_from_updated_vector(updated_query_vec, vectorizer)

    return ' '.join(top_keywords)