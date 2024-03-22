import pandas as pd

# Load your actors database into a DataFrame
actors_df = pd.read_csv('celeb_info.csv')  # Replace with your file path

# This will store the names of the entries we're going to remove
removed_entries = []

# Go through each person and remove the ones with a summary that starts with "may refer to"
for index, row in actors_df.iterrows():
    if (" may refer") in row['Wikipedia Summary']:
        removed_entries.append(row['Celebrity Name'])
        actors_df.drop(index, inplace=True)

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