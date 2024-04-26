from transformers import BertModel, BertTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


def calculate_match_score(partner_traits, celeb_traits):
    if partner_traits == "" or celeb_traits == "":
        return 0.0  
    
    # Tokenize input traits
    partner_tokens = tokenizer(partner_traits, return_tensors='pt', padding=True, truncation=True)
    celeb_tokens = tokenizer(celeb_traits, return_tensors='pt', padding=True, truncation=True)
    
    # Get BERT embeddings for input traits
    with torch.no_grad():
        partner_output = model(**partner_tokens)
        celeb_output = model(**celeb_tokens)
    
    # Extract embeddings
    partner_embedding = partner_output.last_hidden_state.mean(dim=1).numpy()
    celeb_embedding = celeb_output.last_hidden_state.mean(dim=1).numpy()
    
    # Calculate cosine similarity
    score = cosine_similarity(partner_embedding, celeb_embedding)
    
    print("traits", partner_traits, celeb_traits)
    print()
    print("score:", score)
    
    return score[0][0]


partner_traits = ["kind", "funny", "loving"]
celeb_traits = ["compassionate", "charismatic", "intelligent"]

calculate_match_score(partner_traits, celeb_traits)
