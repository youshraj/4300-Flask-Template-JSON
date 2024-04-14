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

def find_top_matches(user_preferences, celebrities_data, top_n=15):
    # Read the data from the DataFrame
    celebrities_df = pd.read_csv(celebrities_data)

    match_scores = []
    for index, row in celebrities_df.iterrows():
        celeb_traits = row['gender'].split(', ') + row['profession'].split(', ') + row['Character Traits'].split(', ')
        total_match_score = calculate_match_score(user_preferences['partner_traits'], celeb_traits)
    
        match_scores.append((row['Celebrity Name'], row['Wikipedia Summary'], row['Personal Life'], row['Image URL'], row['gender'], row['profession'], row['Character Traits'], total_match_score))
    
    match_scores.sort(key=lambda x: x[7], reverse=True)
    
    # Select top 15 matching celebrities
    top_celebrities = match_scores[:15]
    top_celebrities_df = pd.DataFrame(top_celebrities, columns=['Celebrity Name', 'Wikipedia Summary', 'Personal Life', 'Image URL', 'Gender', 'Profession', 'Character Traits', 'Match Score'])

    # Save top 15 matching celebrities and all columns to a CSV file
    top_celebrities_df.to_csv('backend/data/top_matching_celebrities.csv', index=False)

    return top_celebrities
    

celebrities_data = '/Users/bigdelle/Desktop/4300-Flask-Template-JSON/backend/data/final_celeb_info.csv'

#top_matches = find_top_matches(user_preferences, celebrities_data)
