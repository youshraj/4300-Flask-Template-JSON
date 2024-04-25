import json
import os
import csv
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
import Levenshtein as lev
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from user_preferences_utils import calculate_match_score
from rocchios import update_query_vector
import urllib.parse
from flask import jsonify
import numpy as np
import os
from svd import svd

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

app.secret_key = b'e\x9e\xff`1\xc4\xa6H\x81\x0e\xf2\xc4\xbe\x93\xc5\x8a\x17\x13\xf4\xb8\x9bt\x19;'

# Load actors database
def load_actors_database():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_directory, 'data/final_celeb_info.csv')
    return pd.read_csv(csv_file_path)

actors_df = load_actors_database()

def svd_search(actors_df, query, user_traits, top_n):
    user_preferences = session.get('user_preferences', {})
    interest = user_preferences.get("interest", "both")

    if interest == 'men':
        filtered_df = actors_df[actors_df['gender'] == 'male']
    elif interest == 'women':
        filtered_df = actors_df[actors_df['gender'] == 'female']
    else:
        filtered_df = actors_df  
    
    query = query + user_traits #can add profession to query also
    return svd(filtered_df, query, top_n)


def cosine_similarity_search(query, user_traits, top_n, output):
    user_preferences = session.get('user_preferences', {})
    interest = user_preferences.get("interest", "both")

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

    top_indices = similarity_scores.flatten().argsort()[-top_n:][::-1] 

    top_matches = filtered_df.iloc[top_indices]

    if not output:
        top_matches['reasoning'] = ""
        top_matches['match_score'] = 0
    else:
        top_matches['match_score'] = top_matches.apply(
            lambda row: calculate_match_score(user_traits, row['Character Traits']),
            axis=1
        )
        top_matches['reasoning'] = top_matches.apply(
            lambda row: f"You are interested in {user_traits} and this celebrity is described as {row['Character Traits']}.", axis=1
        )
    
    common_words_list = [[] for _ in range(top_n)]

    partner_traits = user_preferences.get("partner_traits", [])


    if isinstance(partner_traits, str):
        try:
            partner_traits = partner_traits.split(',')
        except ValueError: 
            pass 

    #partner_traits = partner_traits.split(',')
    common_words_list = []

    if partner_traits:
        for summary in top_matches['Character Traits']:
            common_words_for_summary = set() 
            clean_summary = summary.strip().rstrip(',').rstrip('.').lower()
            word_list = clean_summary.split(',')
            cleaned_words = [word.strip() for word in word_list]
            summary_words = set(cleaned_words)

            
            for trait in partner_traits:
                trait_words = set(trait.lower().split()) 
                common_words = summary_words.intersection(trait_words)
                
                if common_words:
                    common_words_for_summary.update(common_words)
            
            if common_words_for_summary:
                common_words_list.append(list(common_words_for_summary))
            else:
                common_words_list.append(['None']) 

        top_matches['common_words'] = common_words_list
    else:
        top_matches['common_words'] = [['None'] for _ in range(len(top_matches))]

    selected_columns = ['Celebrity Name', 'Wikipedia Summary', 'Image URL', 'gender', 'profession', 'reasoning', 'match_score', 'common_words', 'Interest Score']
    top_matches = top_matches[selected_columns]
    return jsonify(top_matches.to_dict(orient='records'))

# get profiles for swiping
def profiles():
    actors_data = []
    with open('backend/data/final_celeb_info.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            actors_data.append({
                'Name': row['Celebrity Name'],
                'Summary': row['Wikipedia Summary'],
                'PersonalLife': row['Personal Life'],
                'Image': row['Image URL'],
                'gender': row['gender'],
                'profession': row['profession'],
                'character Traits': row['Character Traits']
            })
    return jsonify(actors_data) 

# sample search using json with pandas
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
    # extract prefs 
    interest = request.form['interest']
    user_traits = request.form['user_traits']
    partner_traits = request.form['partner_traits']

    session['user_preferences'] = {
        'interest': interest,
        'user_traits': user_traits,
        'partner_traits': partner_traits
    }

    return redirect(url_for('home'))  

@app.route("/")
def home():
    preferences = session.get('user_preferences', None)
    return render_template('base.html',title="home page", preferences=preferences)

@app.route('/swipe')
def swipe_page():
    return render_template('swipe.html')

@app.route('/get_updated_matches')
def get_updated_matches():
    user_preferences = session.get('user_preferences', {})
    updated_query_global  = session.get('updated_query_global', "")
    updated_matches = cosine_similarity_search(updated_query_global, user_preferences.get("partner_traits", []), 5, True)
    return updated_matches

@app.route('/output')
def output_page():
    updated_query_global = session.get('updated_query_global', None)
    user_preferences = session.get('user_preferences', {})
    if updated_query_global:
        updated_matches = cosine_similarity_search(updated_query_global, user_preferences.get("partner_traits", []), 5, True)
        return render_template('output.html', matches=updated_matches)
    else:
        return "No updated query available."
    
@app.route("/actors")
def actors_search():
    query = request.args.get("query")
    session['current_query'] = query
    user_preferences = session.get('user_preferences', {})

    # get partner prefs
    partner_traits = user_preferences.get("partner_traits", "")

    if partner_traits:
        return cosine_similarity_search(query, partner_traits, 15, False)
    else:
        return cosine_similarity_search(query, "", 15, False)

@app.route("/get_profiles")
def get_profiles():
    return profiles()

@app.route('/swipe', methods=['POST'])
def handle_swipe():
    current_query = session.get('current_query', None)
    data = request.get_json()
    liked_names = data.get('likes', []) 
    disliked_names = data.get('dislikes', [])
    celeb_df = load_actors_database()

    updated_query = update_query_vector(current_query, liked_names, disliked_names, celeb_df)

    session['current_query'] = updated_query
    session['updated_query_global'] = updated_query

    return jsonify({"message": "Query vector updated successfully", "updated_query": updated_query})


if 'DB_NAME' not in os.environ:
    app.run(debug=True,host="0.0.0.0",port=5000)