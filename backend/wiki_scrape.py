import wikipediaapi

celeb_to_summary_dict = {}

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


celeb_names = ["Tom Hanks", "Ariana Grande"] #expand to 1000 names
for celeb_name in celeb_names:
    summary = get_celeb_info(celeb_name)
    if summary:
        celeb_to_summary_dict[celeb_name] = summary
        # print(f"{celeb_name} Summary:")
        # print(summary)
    else:
        print(f"No information for {celeb_name} on Wikipedia.")
# print(celeb_to_summary_dict)