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

def sanitize_str(str_to_clean, max_length=100):
    #delete & replace invalid char
    invalid_chars = ':*?"<>|/\\'
    for char in invalid_chars:
        str_to_clean = str_to_clean.replace(char, '_')
    
    # limit the size of the text
    if len(str_to_clean) > max_length:
        str_to_clean = str_to_clean[:max_length]
    
    str_to_clean = str_to_clean.strip()
    
    return str_to_clean

def get_categories(url_website):
    
    try:
        # Try to connect to the website 
        response = requests.get(url_website, timeout=10)
        
        if response.status_code == 200:
            # Parse the HTML of the homepage
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Searching container with categories's menu
            bloc_category = soup.find('div', class_="side_categories")
            
            if bloc_category:
                # Extract the list of URL's Categories
                ul_elements = bloc_category.find('ul', class_='nav nav-list')
                url_cat = ul_elements.find_all('a')
                
                # Loop on each category (we just skip "Books")
                for cat in url_cat[1:]:
                    # Extracting name and URL's category
                    category_name = cat.text.strip()
                    category_url = "http://books.toscrape.com/" + cat['href']
                    
                    print(f"Début du scraping pour la catégorie : {category_name}")
                    
                    # Scraping all books from a category
                    get_books_from_category(category_name, category_url)
                    
                    print(f"Scraping de la catégorie {category_name} terminé. ")
        else:
            print(f"Erreur de requête pour {url_website}: "
                  f"Le code de statut est {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion pour {url_website}: {e}")
        return None



def get_books_from_category(category_name, url_cat):
    next_page_url = url_cat 
    #loop while we have "next page" button
    while next_page_url:
        try:
            response = requests.get(next_page_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                #catch all containers with book and call get data function
                book_containers = soup.find_all('h3')
                for container in book_containers:
                    relative_url = container.find('a')['href']
                    full_url = ("http://books.toscrape.com/catalogue/" + relative_url.replace('../../', '').replace('../', ''))
                    get_data_from_book(category_name, full_url)
                
                #identify if we have 'next button'
                next_button = soup.find('li', class_='next')
                if next_button:
                    relative_next_url = next_button.find('a')['href']
                    next_page_url = "/".join(next_page_url.split('/')[:-1]) + "/" + relative_next_url
                else:
                    next_page_url = None
            else:
                print(f"Erreur de requête pour la page : {next_page_url}, "
                      f"code de statut : {response.status_code}")
                next_page_url = None
                
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion pour la page : {next_page_url}, Erreur : {e}")
            next_page_url = None

def get_data_from_book(category_name, url_book):
    response = requests.get(url_book, timeout=10)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        book_data = {}
        
        # --- URL de la page produit ---
        book_data['product_page_url'] = url_book

        # --- Title Extraction ---
        title_element = soup.find('h1')
        book_data['title'] = title_element.text.strip()

        # --- Category ---
        book_data['category'] = category_name

        # --- Product Information Table Extraction ---
        product_table = soup.find('table', class_='table table-striped')
        
        #Check the product table to identify the carac to insert in book_data
        if product_table:
            rows = product_table.find_all('tr')
            
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                
                if th and td:
                    field_name = th.text.strip()
                    field_value = td.text.strip()
                    
                    if field_name == "UPC":
                        book_data['universal_product_code'] = field_value
                    elif field_name == "Price (excl. tax)":
                        book_data['price_excluding_tax'] = field_value.replace('£', '').strip()
                    elif field_name == "Price (incl. tax)":
                        book_data['price_including_tax'] = field_value.replace('£', '').strip()
                    elif field_name == "Availability":
                        # Extract the number of books available: "In stock (X available)"
                        match = re.search(r'\((\d+) available\)', field_value)
                        if match:
                            book_data['number_available'] = match.group(1)
                        else:
                            book_data['number_available'] = "0"

        # --- Description Extraction ---
        description_element = soup.find('div', id='product_description')
        if description_element:
            description_p = description_element.find_next_sibling('p')
            if description_p:
                book_data['product_description'] = description_p.text.strip()
            else:
                book_data['product_description'] = ""
        else:
            book_data['product_description'] = ""

        # --- Rating Extraction ---
        rating_element = soup.find('p', class_=re.compile(r'star-rating'))
        if rating_element:
            rating_class = rating_element.get('class')
            for cls in rating_class:
                if cls in ['One', 'Two', 'Three', 'Four', 'Five']:
                    book_data['review_rating'] = cls
                    break
            else:
                book_data['review_rating'] = ""
        else:
            book_data['review_rating'] = ""

        # --- Image URL Extraction ---
        img_element = soup.find('img')
        if img_element:
            url_relative = img_element['src'].replace('../../', '')
            img_url = 'http://books.toscrape.com/' + url_relative
            book_data['image_url'] = img_url
            
            # Prepare name file and call function download_image
            file_name = book_data['title'].replace("'", "").replace("&", "and")
            file_name = sanitize_str(file_name)
            file_name = re.sub('_+', '_', file_name) + '.jpg'
            download_image(img_url, file_name, category_name)
        else:
            book_data['image_url'] = ""
        
        save_to_csv(book_data, category_name)
    
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
    
    # Building headers
    field_names = [
        'product_page_url',
        'universal_product_code',
        'title', 
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url'
    ]
    
    if book_data:
        # Create folder if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists to know if we need to write header
        file_exists = file_path.exists()
        
        # Write to the csv document
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the single book data
            writer.writerow(book_data)  
            
        print(f"Livre ajouté au CSV : {book_data['title']}")
    else:
        print(f"Aucune donnée à sauvegarder pour la catégorie '{category}'.")

# -----------------------------------------------
# MAIN ENTRY POINT
#------------------------------------------------
if __name__ == "__main__":
    url_site = "https://books.toscrape.com"
    get_categories(url_site)