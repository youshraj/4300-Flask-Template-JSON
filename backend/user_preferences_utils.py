from sentence_transformers import SentenceTransformer, util
import pandas as pd

# Load pre-trained sentence-transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(partner_traits, celeb_traits):
    if partner_traits == [] or celeb_traits == []:
        return 0.0  
    user_embedding = model.encode(partner_traits, convert_to_tensor=True)
    celeb_embedding = model.encode(celeb_traits, convert_to_tensor=True)
    
    score = util.pytorch_cos_sim(user_embedding, celeb_embedding)
    return score[0][0].item()  

    

