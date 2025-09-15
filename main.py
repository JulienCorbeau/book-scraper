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

def get_books_from_category(url_cat):
    """
    Collects a list with all the URLs of books in a category

    
    """
    next_page_url = url_cat 
    
    # Loop while we have a next button
    while next_page_url:
        try:
            # Requesting the first page of the category
            response = requests.get(next_page_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Searching all containers with a book (<h3>)
                book_containers = soup.find_all('h3')
                
                # Extract the URL of the book
                for container in book_containers:
                    relative_url = container.find('a')['href']
                    
                    # Building full Url of a book
                    # delete "../" & "../../" 
                    full_url = ("http://books.toscrape.com/catalogue/" + relative_url.replace('../../', '').replace('../', ''))
                    get_data_from_book(full_url)
                
                # We search a next button
                next_button = soup.find('li', class_='next')
                if next_button:
                    # Building URL next page
                    relative_next_url = next_button.find('a')['href']
                    next_page_url = "/".join(next_page_url.split('/')[:-1]) + "/" + relative_next_url
                else:
                    # No "next button", we continu
                    next_page_url = None
            else:
                print(f"Erreur de requête pour la page : {next_page_url}, "
                      f"code de statut : {response.status_code}")
                next_page_url = None
                
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion pour la page : {next_page_url}, Erreur : {e}")
            next_page_url = None
    
def get_data_from_book(url_book):
    response = requests.get(url_book, timeout=10)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        book_data = {}
        book_category = "Fiction"        
        
        # --- Title Extraction ---
        title_element = soup.find('h1')
        book_data['title'] = title_element.text

        # --- Price Extraction ---
        prix_element = soup.find('p', class_='price_color')
        book_data['price'] = prix_element.text.replace('Â£', '').replace('£', '')

        # --- URL's image Extraction and prepare image's name---
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
        
        # Check if file exists to know if we need to write header
        file_exists = file_path.exists()
        
        # Write to the csv document in APPEND mode
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the single book data
            writer.writerow(book_data)  
            
        print(f"Livre ajouté au CSV : {book_data['title']}")
    else:
        # If book has no category
        print(f"Aucune donnée à sauvegarder pour la catégorie '{category}'.")
# -----------------------------------------------
# MAIN ENTRY POINT
#------------------------------------------------
if __name__ == "__main__":
    url_site = "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
    get_books_from_category(url_site)