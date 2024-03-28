import pandas as pd
import re

def determine_gender(summary):
    male_pronouns = sum(summary.lower().count(pronoun) for pronoun in [' he ', ' him ', ' his '])
    female_pronouns = sum(summary.lower().count(pronoun) for pronoun in [' she ', ' her ', ' hers '])
    total_pronouns = male_pronouns + female_pronouns

    if total_pronouns == 0:
        return 'unclear'
    elif male_pronouns / total_pronouns > 0.8:
        return 'male'
    elif female_pronouns / total_pronouns > 0.8:
        return 'female'
    else:
        return 'unclear'

def extract_profession(summary):
    match = re.search(r'\b(is|was)\b\s+([^.]+)', summary)
    if match:
        profession = match.group(2).strip()
        # Remove leading articles ("a", "an", "the")
        profession = re.sub(r'^(a|an|the)\s+', '', profession, flags=re.I)
        return profession
    else:
        return ""

# Load the actors database into a DataFrame
actors_df = pd.read_csv('celeb_info.csv')  # Replace with your file path

# This will store the names of the entries we're going to remove
removed_entries = []

# Go through each person and remove the ones with a summary that starts with "may refer to"
for index, row in actors_df.iterrows():
    if " may refer" in row['Wikipedia Summary']:
        removed_entries.append(row['Celebrity Name'])
        actors_df.drop(index, inplace=True)

# Add a 'gender' and 'profession' column
actors_df['gender'] = actors_df['Wikipedia Summary'].apply(determine_gender)
actors_df['profession'] = actors_df['Wikipedia Summary'].apply(extract_profession)

# Reset the index of the resulting DataFrame
actors_df.reset_index(drop=True, inplace=True)

# Save the cleaned DataFrame back to a CSV file
actors_df.to_csv('cleaned_celeb_info.csv', index=False)  # Replace with your desired file path

# Output the names of the removed entries
print(removed_entries)
# Open a file in write mode ('w')
with open('removed_entries.txt', 'w') as file:
    # Write each item in the list to the file
    for item in removed_entries:
        file.write('%s\n' % item)