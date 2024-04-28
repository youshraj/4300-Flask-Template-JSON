from sentence_transformers import SentenceTransformer, util
import pandas as pd
import math
import numpy as np
import random

model = SentenceTransformer('bert-base-nli-mean-tokens')

def calculate_match_score(partner_traits, celeb_traits, celeb_pop, desired_pop,popularity =True):
     if partner_traits == "" or celeb_traits == "":
         return 0.0  
     user_embedding = model.encode(partner_traits, convert_to_tensor=True)
     celeb_embedding = model.encode(celeb_traits, convert_to_tensor=True)
     score = util.pytorch_cos_sim(user_embedding, celeb_embedding)
    #  print(partner_traits, celeb_traits)
    #  print(score)
     if popularity:
        score_updated_popularity = match_with_popularity(score[0][0].item(), celeb_pop, desired_pop)
        return score_updated_popularity 
     return score

def calculate_reasoning(partner_traits, celeb_traits, celeb_name):

    if not partner_traits or not celeb_traits:
        return "Missing traits information."

    partner_traits_list = partner_traits.split(", ")
    celeb_traits_list = celeb_traits.split(", ")

    if len(partner_traits_list) < 2 or len(celeb_traits_list) < 2:
        return "This celebrity's traits are very similar to those you prefer!"
    
    p1 = random.sample(partner_traits_list,1)[0]
    p2 = random.sample(partner_traits_list,1)[0]
    while p1 == p2:
        p2 = random.sample(partner_traits_list,1)[0]
    
    c1 = random.sample(celeb_traits_list,1)[0]
    c2 = random.sample(celeb_traits_list,1)[0]
    while c1 == c2:
        c2 = random.sample(celeb_traits_list,1)[0]
    
    

    user_embedding = model.encode(p1, convert_to_tensor=True)
    celeb_embedding = model.encode(c1, convert_to_tensor=True)
    score1 = float(util.pytorch_cos_sim(user_embedding, celeb_embedding))

    user_embedding = model.encode(p2, convert_to_tensor=True)
    celeb_embedding = model.encode(c2, convert_to_tensor=True)
    score2 = float(util.pytorch_cos_sim(user_embedding, celeb_embedding))
    
    avg = float((score1 + score2) / 2.0)

    if avg > 0.75:
        reasoning_message = "You guys would be a great match!"
    elif avg > 0.5:
        reasoning_message = "I sense some chemistry!"
    else:
        reasoning_message = "It seems like this could go somewhere..."

    response_message = (f"You wanted someone {p1} and {p2}, and {celeb_name} is described as {c1} and {c2}. "
                        f"{reasoning_message}")
    
    return response_message

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