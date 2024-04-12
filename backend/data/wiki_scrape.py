import wikipediaapi
import requests
import csv

celeb_to_summary_dict = {}
celeb_to_imgs_dict = {}

def get_all_section_text(section):
    """
    Recursively collects text from a section and its subsections.
    """
    text = section.text + "\n"  
    for subsection in section.sections:
        text += get_all_section_text(subsection)
    return text

def get_celeb_info(celeb_name):
    # Initialize Wikipedia API
    wiki_wiki = wikipediaapi.Wikipedia('Chronomingle (brb227@cornell.edu)', 'en')
    page = wiki_wiki.page(celeb_name)
    if page.exists():
        summary = page.summary
        personal_life_section = page.section_by_title("Personal life")
        if personal_life_section:
            # Now get all text, including subsections
            personal_life_text = get_all_section_text(personal_life_section)
        else:
            personal_life_text = "No 'Personal Life' section available."
        return summary, personal_life_text
    else:
        return None
    
def get_celeb_url(celeb_name):
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={celeb_name}&pithumbsize=300"
    response = requests.get(url)

    data = response.json()
    pages = data.get('query', {}).get('pages', {})
    for page_id, page_info in pages.items():
        thumbnail_info = page_info.get('thumbnail')
        if thumbnail_info:
            return thumbnail_info.get('source')

    return None

def read_celeb_names_from_file(file_path):
    with open(file_path, 'r') as file:
        celeb_names = [line.strip() for line in file]
    return celeb_names

def write_to_csv(celeb_data, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Include 'Personal Life' in the header row
        writer.writerow(['Celebrity Name', 'Wikipedia Summary', 'Personal Life', 'Image URL'])
        for celeb_name, data in celeb_data.items():
            # Ensure to include data.get('personal_life', '') in the row
            writer.writerow([celeb_name, data.get('summary', ''), data.get('personal_life', ''), data.get('image', '')])
celeb_names_file = "celeb_input.txt"
celeb_names = read_celeb_names_from_file(celeb_names_file)

# Initialize an empty dictionary to collect data for celebrities with complete info
complete_celeb_info = {}

for celeb_name in celeb_names:
    celeb_info = get_celeb_info(celeb_name)  # Get celeb info without unpacking immediately
    url = get_celeb_url(celeb_name)

    # Check if celeb_info is not None before attempting to unpack
    if celeb_info is not None:
        summary, personal_life_text = celeb_info
    else:
        summary, personal_life_text = None, None

    # Proceed only if all pieces of information are present
    if summary and personal_life_text and url:
        # If everything is present, add to the dictionary
        complete_celeb_info[celeb_name] = {
            'summary': summary,
            'personal_life': personal_life_text,
            'image': url
        }
    else:
        # Determine which pieces of information are missing for clearer messaging
        missing_elements = [elem for elem, value in {"summary": summary, "personal life section": personal_life_text, "image": url}.items() if not value]
        print(f"Skipping {celeb_name} due to missing: {', '.join(missing_elements)}")

csv_file_path = "celeb_info.csv"
write_to_csv(complete_celeb_info, csv_file_path)

print("Data written to CSV successfully!")
