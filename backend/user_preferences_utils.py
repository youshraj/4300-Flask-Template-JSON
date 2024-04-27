from sentence_transformers import SentenceTransformer, util
import pandas as pd
import math

model = SentenceTransformer('bert-base-nli-mean-tokens')

def calculate_match_score(partner_traits, celeb_traits, celeb_pop, desired_pop):
     if partner_traits == "" or celeb_traits == "":
         return 0.0  
     user_embedding = model.encode(partner_traits, convert_to_tensor=True)
     celeb_embedding = model.encode(celeb_traits, convert_to_tensor=True)
     score = util.pytorch_cos_sim(user_embedding, celeb_embedding)
     print(partner_traits, celeb_traits)
     print(score)
     score_updated_popularity = match_with_popularity(score[0][0].item(), celeb_pop, desired_pop)
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
print(adj_score)
'''