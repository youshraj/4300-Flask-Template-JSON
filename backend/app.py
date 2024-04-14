import json
import os
import csv
from flask import Flask, render_template, request, redirect, url_for,jsonify
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import Levenshtein as lev
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from user_preferences_utils import calculate_match_score
import urllib.parse
from flask import jsonify

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

current_directory = os.path.dirname(os.path.abspath(__file__))

json_file_path = os.path.join(current_directory, 'init.json')

# Assuming your JSON data is stored in a file named 'init.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)
    episodes_df = pd.DataFrame(data['episodes'])
    reviews_df = pd.DataFrame(data['reviews'])

app = Flask(__name__)
CORS(app)

user_preferences = {}

# Load actors database
def load_actors_database():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_directory, 'data/final_celeb_info.csv')
    return pd.read_csv(csv_file_path)

actors_df = load_actors_database()

def cosine_similarity_search(query, user_traits):
    interest = user_preferences.get('interest', 'both')

    if interest == 'men':
        filtered_df = actors_df[actors_df['gender'] == 'male']
    elif interest == 'women':
        filtered_df = actors_df[actors_df['gender'] == 'female']
    else:
        filtered_df = actors_df  

    # vectorize  data
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(filtered_df['profession'])

    query_vector = tfidf_vectorizer.transform([query])
    similarity_scores = cosine_similarity(tfidf_matrix, query_vector)

    top_indices = similarity_scores.flatten().argsort()[-25:][::-1]  # Adjust number as needed

    top_matches = filtered_df.iloc[top_indices]

    top_matches['reasoning'] = similarity_scores.flatten()[top_indices]

    if user_traits != "":
        top_matches['match_score'] = top_matches.apply(
            lambda row: calculate_match_score(user_traits, row['Character Traits']),
            axis=1
        )
    else:
        top_matches['match_score'] = 0

    selected_columns = ['Celebrity Name', 'Wikipedia Summary', 'Image URL', 'gender', 'profession', 'reasoning', 'match_score']
    top_matches = top_matches[selected_columns]

    # Convert DataFrame to JSON and return
    return jsonify(top_matches.to_dict(orient='records'))

    
# Sample search using json with pandas
def json_search(query):
    matches = []
    merged_df = pd.merge(episodes_df, reviews_df, left_on='id', right_on='id', how='inner')
    matches = merged_df[merged_df['title'].str.lower().str.contains(query.lower())]
    matches_filtered = matches[['title', 'descr', 'imdb_rating']]
    matches_filtered_json = matches_filtered.to_json(orient='records')
    return matches_filtered_json

@app.route('/preferences', methods=['GET'])
def show_preferences_form():
    return render_template('preferences.html')

@app.route('/save_preferences', methods=['POST'])
def save_preferences():
    global user_preferences
    # extract prefs 
    interest = request.form['interest']
    user_traits = request.form['user_traits'].split(',')
    partner_traits = request.form['partner_traits'].split(',')

    user_preferences = {
        'interest': interest,
        'user_traits': user_traits,
        'partner_traits': partner_traits
    }

    # Redirect to the home page
    return redirect(url_for('home'))  

@app.route("/")
def home():
    return render_template('base.html',title="home page", preferences=user_preferences)

@app.route('/swipe')
def swipe_page():
    return render_template('swipe.html')

@app.route('/output')
def output_page():
    return render_template('output.html')

@app.route("/actors")
def actors_search():
    query = request.args.get("query")
    if user_preferences:
        return cosine_similarity_search(query, user_preferences["partner_traits"])
    else:
        return cosine_similarity_search(query, "")

@app.route("/get_profiles")
def get_profiles():
    actors_data = []

    with open('backend/data/final_celeb_info.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            actors_data.append({
                'Name': row['Celebrity Name'],
                'Summary': row['Wikipedia Summary'],
                'PersonalLife': row['Personal Life'],
                'Image': row['Image URL'],
                'Gender': row['gender'],
                'Profession': row['profession'],
                'CharacterTraits': row['Character Traits']
            })
    return jsonify(actors_data)

if 'DB_NAME' not in os.environ:
    app.run(debug=True,host="0.0.0.0",port=5000)