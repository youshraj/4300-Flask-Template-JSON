from sentence_transformers import SentenceTransformer, util

# load pre-trained sentence-transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(partner_traits, celeb_traits):
    
    # encode the traits
    user_embedding = model.encode(partner_traits, convert_to_tensor=True)
    celeb_embedding = model.encode(celeb_traits, convert_to_tensor=True)
    
    # cosine similarity
    score = util.pytorch_cos_sim(user_embedding, celeb_embedding)
    
    return score.item()  # return similarity score

# example
user_traits = "adventurous, funny, outgoing"
user_preferences = {
    'interest': 'women',
    'partner_traits': "creative, intelligent"
}
celeb_traits = "artistic, humorous, extroverted"

match_score = calculate_match_score(user_preferences['partner_traits'], celeb_traits)
print(f"Match Score: {match_score}")
