from sentence_transformers import SentenceTransformer, util
import pandas as pd

# Load pre-trained sentence-transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(partner_traits, celeb_traits):
    # Encode the traits
    user_embedding = model.encode(partner_traits, convert_to_tensor=True)
    celeb_embedding = model.encode(celeb_traits, convert_to_tensor=True)
    
    # Cosine similarity
    score = util.pytorch_cos_sim(user_embedding, celeb_embedding)
    
    return score[0][0].item()  # Return similarity score

def find_top_matches(user_preferences, top_n=15):
    # Read the data from the DataFrame
    celebrities_df = pd.read_csv('backend/data/final_celeb_info.csv')

    
    partner_traits = user_preferences['partner_traits']
    # Calculate match score for each celebrity
    celebrities_df['match_score'] = celebrities_df['Character Traits'].apply(lambda x: calculate_match_score(partner_traits, x))
    
    # Sort celebrities by match score in descending order
    top_celebrities = celebrities_df.sort_values(by='match_score', ascending=False).head(15)
    top_celebrities.to_csv('backend/data/top_matching_celebrities.csv', index=False)
    return top_celebrities

    

