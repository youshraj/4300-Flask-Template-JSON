import numpy as np
import pandas as pd

# Read the data from the CSV file into a DataFrame
celebrities_df = pd.read_csv('backend/data/top_matching_celebrities.csv')

# User traits and preferences
user_traits = ["adventurous", "funny", "outgoing"]
user_preferences = {
    'interest': 'women',
    'partner_traits': ["creative", "intelligent"]
}

# Initialize Rocchio vector
rocchio_vector = np.zeros(len(user_traits))

# Iterate through celebrities, limiting to 15
num_celebrities = min(15, len(celebrities_df))
for index, row in celebrities_df.head(num_celebrities).iterrows():
    print(f"\nCelebrity Name: {row['Celebrity Name']}")
    print(f"Wikipedia Summary: {row['Wikipedia Summary']}")
    print(f"Personal Life: {row['Personal Life']}")
    print(f"Image URL: {row['Image URL']}")
    print(f"Gender: {row['Gender']}")
    print(f"Profession: {row['Profession']}")
    print(f"Character Traits: {row['Character Traits']}")
    
    opinion = int(input("What do you think about this celebrity? (1: strongly dislike, 2: dislike, 3: neutral, 4: like, 5: strongly like): "))

    if opinion < 3:
        opinion_vector = np.array([-1] * len(user_traits))
    elif opinion > 3:
        opinion_vector = np.array([1] * len(user_traits))
    else:
        opinion_vector = np.zeros(len(user_traits))

    # Update Rocchio vector
    rocchio_vector += opinion_vector

# Apply Rocchio's algorithm to find the ideal celebrity
for trait in user_traits:
    if trait in user_preferences['partner_traits']:
        rocchio_vector[user_traits.index(trait)] += 1
    if trait in user_preferences['interest']:
        rocchio_vector[user_traits.index(trait)] += 1

# Find the celebrity closest to the ideal vector
min_distance = float('inf')
ideal_celeb = None
for index, row in celebrities_df.head(num_celebrities).iterrows():
    celeb_vector = np.zeros(len(user_traits))
    celeb_traits = row['Gender'].split(', ') + row['Profession'].split(', ') + row['Character Traits'].split(', ')
    for trait in celeb_traits:
        if trait in user_preferences:
            celeb_vector[user_traits.index(trait)] = 1
    distance = np.linalg.norm(rocchio_vector - celeb_vector)
    if distance < min_distance:
        min_distance = distance
        ideal_celeb = row['Celebrity Name']

print(f"\nIdeal celebrity for you is: {ideal_celeb}")