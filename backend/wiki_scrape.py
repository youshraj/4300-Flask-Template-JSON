import wikipediaapi
import requests

celeb_to_summary_dict = {}
celeb_to_imgs_dict = {}

def get_celeb_info(celeb_name):
    # Initialize Wikipedia API
    wiki_wiki = wikipediaapi.Wikipedia('chronoMingleClassProj/0.1 (ars369@cornell.edu)', 'en')

    page = wiki_wiki.page(celeb_name)

    if page.exists():
        #main_text = page.text
        #can also get entirety of article with main_text
        summary = page.summary

        return summary
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

celeb_names_file = "4300-Flask-Template-JSON/backend/celeb_input.txt"  # Path to the text file containing celebrity names
celeb_names = read_celeb_names_from_file(celeb_names_file)
for celeb_name in celeb_names:
    summary = get_celeb_info(celeb_name)
    url = get_celeb_url(celeb_name)
    if summary:
        celeb_to_summary_dict[celeb_name] = summary
        # print(f"{celeb_name} Summary:")
        # print(summary)
    else:
        print(f"No summary for {celeb_name} on Wikipedia.")
    if url:
        celeb_to_imgs_dict[celeb_name] = url
    else:
        print(f"No image for {celeb_name} on Wikipedia")
print(celeb_to_summary_dict)
# print(celeb_to_imgs_dict)

