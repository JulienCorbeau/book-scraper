# ------------------------------------------------------
# IMPORTS
# ------------------------------------------------------

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import re

# ------------------------------------------
#FUNCTIONS 
# ---------------------------------------------

def sanitize_str(str_to_clean):
    invalid_chars = ':*?"<>|/\\'
    for char in invalid_chars:
        str_to_clean = str_to_clean.replace(char, '_')
    return str_to_clean

def get_data_from_book(url_book):
    response = requests.get(url_book, timeout=10)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.find('h1')
        book_data = {}
        book_category = "Travel"
        book_data['title'] = title_element.text
        prix_element = soup.find('p', class_='price_color')
        book_data['price'] = prix_element.text.replace('Â£', '').replace('£', '')
        img_element = soup.find('img')
        url_relative = img_element['src'].replace('../../', '')
        img_url = 'http://books.toscrape.com/' + url_relative
        file_name = book_data['title'].replace("'", "").replace("&", "and")
        file_name = sanitize_str(file_name)
        file_name = re.sub('_+', '_', file_name) + '.jpg'
        download_image(img_url, file_name, book_category)
        save_to_csv(book_data, book_category)  
    
def download_image(img_url, file_name, book_category):
    # Building path : data/images/[category]/[file]
    folder_path = Path("data/images") / book_category
    file_path = folder_path / file_name
    try:
        # --- Download picture ---
        response = requests.get(img_url)
                
        if response.status_code == 200:
            # Create folder if it doesn't exist
            folder_path.mkdir(parents=True, exist_ok=True)
                    
            # Save / Write the picture (binary)
            with open(file_path, 'wb') as file:
                file.write(response.content)
                        
            print(f"Image téléchargée avec succès dans {file_path}")
        else:
            print(f"Erreur lors du téléchargement de l'image. "
                f"Code de statut: {response.status_code}")
                        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion lors du téléchargement: {e}")

    
def save_to_csv(book_data, category):
    # Building path of the file
    file_name = f"Scraping_{category}.csv"
    file_path = Path("data/csv") / file_name
    
    # Defining columns to include in CSV
    field_names = ['title', 'price']
    
    if book_data:
        # Create folder if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to the csv document
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            
            # Write header
            writer.writeheader()
            
            # Write the single book data
            writer.writerow(book_data)  
            
        print(f"Les données de la catégorie '{category}' ont été extraites "
                f"et sauvegardées dans {file_path}")
    else:
        # If book has no category
        print(f"Aucune donnée à sauvegarder pour la catégorie '{category}'.")

# -----------------------------------------------
# MAIN ENTRY POINT
#------------------------------------------------
if __name__ == "__main__":
    url_site = "https://books.toscrape.com/catalogue/1000-places-to-see-before-you-die_1/index.html"
    get_data_from_book(url_site)