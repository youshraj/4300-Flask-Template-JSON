import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import Levenshtein as lev
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'init.json')

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)
    episodes_df = pd.DataFrame(data['episodes'])
    reviews_df = pd.DataFrame(data['reviews'])

app = Flask(__name__)
CORS(app)

# Load actors database
def load_actors_database():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_directory, 'data/cleaned_celeb_info.csv')
    return pd.read_csv(csv_file_path)

actors_df = load_actors_database()


def minimum_edit_distance_search(query):
    # Function to calculate combined minimum edit distance to both name and summary
    def calculate_normalized_distance(row, query):
        name = row['Celebrity Name'].lower()
        summary = row['Wikipedia Summary'].lower()
        query = query.lower()
        
        # Calculate edit distances
        name_distance = lev.distance(query, name)
        summary_distance = lev.distance(query, summary)
        
        # Normalize distances by the length of the longer string
        max_name_length = max(len(query), len(name))
        max_summary_length = max(len(query), len(summary))
        
        normalized_name_distance = name_distance / max_name_length if max_name_length else 0
        normalized_summary_distance = summary_distance / max_summary_length if max_summary_length else 0
        
        # Combine the normalized distances
        combined_distance = normalized_name_distance + normalized_summary_distance
        return combined_distance

    # Calculate distance for each actor
    actors_df['normalized_distance'] = actors_df.apply(lambda row: calculate_normalized_distance(row, query), axis=1)

    # Sort by distance and select top 5
    top_matches = actors_df.sort_values(by='normalized_distance').head(5)

    return top_matches[['Celebrity Name', 'Wikipedia Summary', 'Image URL']].to_json(orient='records')

def cosine_similarity_search(query):
    # Pre-process query for gender
    male_keywords = ["man", "male", "men", "boy", "boys", "guy", "guys", "dude", "dudes"]
    female_keywords = ["female", "woman", "women", "girl", "lady", "ladies", "chick", "chicks"]
    gender_filter = None

    contains_male_keyword = any(keyword in query.lower() for keyword in male_keywords)
    contains_female_keyword = any(keyword in query.lower() for keyword in female_keywords)

    # If both male and female keywords are present or none, do not filter by gender
    if contains_male_keyword and contains_female_keyword or not (contains_male_keyword or contains_female_keyword):
        filtered_df = actors_df
    else:
        gender_filter = 'male' if contains_male_keyword else 'female'
        filtered_df = actors_df[actors_df['gender'] == gender_filter]

    # Vectorize the data
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(filtered_df['profession'])

    # Transform query into vector representation
    query_vector = tfidf_vectorizer.transform([query])

    # Calculate cosine similarity between query and all actors in filtered_df
    similarity_scores = cosine_similarity(tfidf_matrix, query_vector)

    # Get indices of top matches
    top_indices = similarity_scores.flatten().argsort()[-5:][::-1]  # Adjust number as needed

    # Get top matches
    top_matches = filtered_df.iloc[top_indices]

    # Select required columns to return
    return top_matches[['Celebrity Name', 'Wikipedia Summary', 'Image URL', 'gender', 'profession']].to_json(orient='records')

# Sample search using json with pandas
def json_search(query):
    matches = []
    merged_df = pd.merge(episodes_df, reviews_df, left_on='id', right_on='id', how='inner')
    matches = merged_df[merged_df['title'].str.lower().str.contains(query.lower())]
    matches_filtered = matches[['title', 'descr', 'imdb_rating']]
    matches_filtered_json = matches_filtered.to_json(orient='records')
    return matches_filtered_json

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route('/swipe.html')
def swipe_page():
    return render_template('swipe.html')

@app.route('/output.html')
def output_page():
    return render_template('output.html')

@app.route("/actors")
def actors_search():
    query = request.args.get("query")
    return cosine_similarity_search(query)

if 'DB_NAME' not in os.environ:
    app.run(debug=True,host="0.0.0.0",port=5000)