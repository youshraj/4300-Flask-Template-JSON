from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer('bert-base-nli-mean-tokens')

def calculate_match_score(partner_traits, celeb_traits):
    if partner_traits == "" or celeb_traits == "":
        return 0.0  
    user_embedding = model.encode(partner_traits, convert_to_tensor=True)
    celeb_embedding = model.encode(celeb_traits, convert_to_tensor=True)
    score = util.pytorch_cos_sim(user_embedding, celeb_embedding)
    print(partner_traits, celeb_traits)
    print(score)
    return score[0][0].item()  


partner_traits = ["kind", "funny", "loving"]
celeb_traits = ["compassionate", "charismatic", "intelligent"]

calculate_match_score(partner_traits, celeb_traits)
