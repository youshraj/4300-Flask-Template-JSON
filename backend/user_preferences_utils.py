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
    if desired_popularity == None:
        return match_score #leave as is
    
    popularity_difference = abs(celeb_popularity - desired_popularity)

    adjustment_factor = 0
    if popularity_difference < 15:
        adjustment_factor += 0.8
    elif popularity_difference < 35:
        adjustment_factor = 0
    elif popularity_difference < 55:
        adjustment_factor -= 0.8
    else:
        adjustment_factor -= 0.15

    adjusted_score = match_score + adjustment_factor
    adjusted_score = max(0, min(adjusted_score, 1))


    return adjusted_score

partner_traits = ["kind", "funny", "loving"]
celeb_traits = ["compassionate", "charismatic", "intelligent"]

score = calculate_match_score(partner_traits, celeb_traits, 70, 65)
# adj_score = match_with_popularity(score, 70, 75)
# print(adj_score)
