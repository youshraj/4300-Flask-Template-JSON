import pandas as pd
from openai import OpenAI
import tqdm

#API Key
client = ""
apiUrl = 'https://api.openai.com/v1/completions';

def get_character_traits(personal_life_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Provide a comma-separated list of 5 to 10 character traits demonstrated in the following personal life description. Avoid numbering them and do not add additional context or explanation:\n\n{personal_life_text}"}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:  # Catch all exceptions
        print(f"Error with OpenAI API call: {e}")
        return None
    
df = pd.read_csv('cleaned_celeb_info.csv')

df['Character Traits'] = ''

for index, row in ttqdm(df.iterrows(), desc="Progress for requests"):
    personal_life_text = row['Personal Life']
    if pd.notna(personal_life_text):  
        traits = get_character_traits(personal_life_text)
        df.at[index, 'Character Traits'] = traits
# Specify the path for the new CSV file
updated_csv_path = 'final_celeb_info.csv'

df.to_csv(updated_csv_path, index=False)

print("Data with character traits written to CSV successfully!")
