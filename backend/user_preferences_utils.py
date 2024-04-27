from sentence_transformers import SentenceTransformer, util
import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

def calculate_sentiment_score(traits):
    # Calculate sentiment score for each trait
    sentiment_scores = [sia.polarity_scores(trait)['compound'] for trait in traits]
    return sentiment_scores

def calculate_match_score(partner_traits, celeb_traits, celeb_pop, desired_pop):
    if partner_traits == "" or celeb_traits == "":
        return 0.0  
    #partner_traits = [trait.strip() for trait in partner_traits.split(',')]
    #celeb_traits = [trait.strip() for trait in celeb_traits.split(',')]
    
    # Calculate sentiment scores for partner and celebrity traits
    partner_sentiment_scores = calculate_sentiment_score(partner_traits)
    celeb_sentiment_scores = calculate_sentiment_score(celeb_traits)
    
    # Pad the shorter vector with zeros to match the length of the longer vector
    max_length = max(len(partner_sentiment_scores), len(celeb_sentiment_scores))
    partner_sentiment_scores += [0] * (max_length - len(partner_sentiment_scores))
    celeb_sentiment_scores += [0] * (max_length - len(celeb_sentiment_scores))
    
    # Calculate cosine similarity between sentiment scores
    score = cosine_similarity([partner_sentiment_scores], [celeb_sentiment_scores])

    print(partner_traits, celeb_traits)
    print(score[0][0])
    score_updated_popularity = match_with_popularity(score[0][0], celeb_pop, desired_pop)
    return score_updated_popularity 

def match_with_popularity(match_score, celeb_popularity, desired_popularity):
    if desired_popularity is None:
        return match_score  # Leave as is

    # define popularity ranges
    popularity_ranges = {
        'low': (0, 20),
        'medium': (21, 55),
        'high': (56, 100)
    }

    celeb_range = None
    for range_name, (lower, upper) in popularity_ranges.items():
        if lower <= celeb_popularity <= upper:
            celeb_range = range_name
            break

    if celeb_range is None:
        return match_score  
    desired_range = desired_popularity.lower() 
    if desired_range == celeb_range:
        adjusted_score = match_score * 1.15
    elif abs(list(popularity_ranges.keys()).index(desired_range) - list(popularity_ranges.keys()).index(celeb_range)) == 1:
        adjusted_score = match_score * 0.95
    elif abs(list(popularity_ranges.keys()).index(desired_range) - list(popularity_ranges.keys()).index(celeb_range)) == 2:
        adjusted_score = match_score * 0.7
    else:
        adjusted_score = match_score
    
    adjusted_score = max(0, min(adjusted_score, 1))
    return adjusted_score



'''partner_traits = ["kind", "funny", "loving"]
celeb_traits = ["compassionate", "charismatic", "intelligent"]

score = calculate_match_score(partner_traits, celeb_traits, 70, 65)
adj_score = match_with_popularity(score, 70, 75)
print(adj_score)'''
