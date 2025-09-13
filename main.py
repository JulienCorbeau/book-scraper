# ------------------------------------------------------
# IMPORTS
# ----------------------------------------------------
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import re


# ------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------

def get_categories(url_website):
    """
   Fetch all categories on the site and start full scraping

    """
    all_books_data = []
    
    try:
        # Try to connect tu the website 
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
                    books_data_from_cat = get_books_from_category(category_name, category_url)
                    
                    # We had the list of one category to the list with all category to save CSV
                    all_books_data.extend(books_data_from_cat)
                    
                    print(f"Scraping de la catégorie {category_name} terminé. "
                          f"{len(books_data_from_cat)} livres récupérés.")
        else:
            print(f"Erreur de requête pour {url_website}: "
                  f"Le code de statut est {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion pour {url_website}: {e}")
        return None
    
    return all_books_data


def get_books_from_category(category_name, url_cat):
    """
    Collects a list with all the URLs of books in a category

    
    """
    books_urls = []  # Create list to store all books's URL
    next_page_url = url_cat 
    
    # Loop while we have a next button
    while next_page_url:
        try:
            # Requesting the first page of the category
            response = requests.get(next_page_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Searching all containers we a book (<h3>)
                book_containers = soup.find_all('h3')
                
                # Extract the URL of the book
                for container in book_containers:
                    relative_url = container.find('a')['href']
                    
                    # Building full Url of a book
                    # delete "../" & "../../" 
                    full_url = ("http://books.toscrape.com/catalogue/" + 
                               relative_url.replace('../../', '').replace('../', ''))
                    books_urls.append(full_url)
                
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
    
    # When we have all URL from category, we use get_data_from_books to extract the data 
    return get_data_from_books(books_urls, category_name)


def get_data_from_books(books_urls, category_name):
    """
    Extract data from all books by a loop and download picture
   
    """
    all_books_data = []
    
    # Loop through each book URL
    for url in books_urls:
        try:
            # We go to the book's page
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8' 
            
            if response.status_code == 200:
                book_data = {}  # Creating dictionnary to store the books's data
                soup = BeautifulSoup(response.text, 'html.parser')

                # --- Title Extraction ---
                title_element = soup.find('h1')
                book_data['title'] = title_element.text
                
                # --- Price Extraction ---
                prix_element = soup.find('p', class_='price_color')
                # Cleaning price                Ensure function ?
                book_data['price'] = prix_element.text.replace('Â£', '')
                
                # --- Create category in book_data  for the csv save ---
                # creation of a variable: "category"
                book_data['category_name'] = category_name
                
                # --- Image extract ---
                img_element = soup.find('img')
                # Building of image's URL
                url_relative = img_element['src'].replace('../../', '')
                img_url = 'http://books.toscrape.com/' + url_relative

                # --- Cleaning file's name --- 
                # TODO: "ensure_valid_filename"
                file_name = book_data['title'].replace("'", "").replace("&", "and")
                
                # Cleaning forbiden char in the file's name                         Ensure Function
                invalid_chars = ':*?"<>|/\\'
                for char in invalid_chars:
                    file_name = file_name.replace(char, '_')
                
                # Cleaning if we have many underscores and add the extension.              Ensure Function ?
                file_name = re.sub('_+', '_', file_name) + '.jpg'
                
                # Calling download image function
                download_image({'img_url': img_url, 'file': file_name}, category_name)

                # Append this book in the list of All Books
                all_books_data.append(book_data)
                
            else:
                print(f"Erreur de requête pour le livre : {url}, "
                      f"code de statut : {response.status_code}")
                      
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion pour le livre : {url}, Erreur : {e}")
            
    return all_books_data


def download_image(book_info, category_name):
    """
    Download & Save picture.
    
    """
    if book_info:
        img_name = book_info['file']
        
        # === PRÉPARATION DU CHEMIN DE DESTINATION ===
        # Cleaning category name               Need to create ensure function
        clean_category_name = (category_name.replace(" ", "_")
                                            .replace(":", "_")
                                            .replace("'", "")
                                            .replace("&", "and"))
        
        # Building path : data/images/[category]/[file]
        folder_path = Path("data/images") / clean_category_name
        file_path = folder_path / img_name

        try:
            # --- Download picture ---
            response = requests.get(book_info['img_url'])
            
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


def save_to_csv(all_scraped_data):
    """
   Save scraped data in the CSV document

    """
    if all_scraped_data:
        # --- SORT BY CATEGORY ---
        books_by_category = {}
        
        for book in all_scraped_data:
            # Vereify category name exist
            if 'category_name' in book:
                category_name = book['category_name']
                
                # Initialisation of list for category (if it's the first book of this category)
                if category_name not in books_by_category:
                    books_by_category[category_name] = []
                    
                books_by_category[category_name].append(book)
            else:
                # If book has category empty
                print(f"Attention: livre sans catégorie trouvé : "
                      f"{book.get('title', 'Titre inconnu')}")

        #---------- Creating CSV Files --------------
        for category_name, books in books_by_category.items():
            # Cleaning category name               Need to create ensure function
            clean_category_name = (category_name.replace(" ", "_")
                                                .replace(":", "_")
                                                .replace("'", "")
                                                .replace("&", "and"))
            
            # Building path of the file
            file_name = f"Scraping_{clean_category_name}.csv"
            file_path = Path("data/csv") / file_name
            
            # Defining columns to include in CSV
            field_names = ['title', 'price']
            
            if books:
                # Create folder if it's didn't exist
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to the csv document
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=field_names, extrasaction='ignore')
                    
                    # Write header
                    writer.writeheader()
                    
                    # Write all datas
                    writer.writerows(books)
                    
                print(f"Les données de la catégorie '{category_name}' ont été extraites "
                      f"et sauvegardées dans {file_path}")
            else:
                # If book has no category
                print(f"Aucune donnée à sauvegarder pour la catégorie '{category_name}'.")
    else:
        print("Aucune donnée à sauvegarder.")


# ---------------------------
# MAIN ENTRY POINT
# --------------------------
if __name__ == "__main__":
    """
    Workflow :
    1. Scrape beginning
    2. Save data in csv
    3. Tell that finish
    """
    # URL to scrape
    url_site = "https://books.toscrape.com/"
    
    print("DÉBUT DU SCRAPING COMPLET")
    
    # Scraping all categories
    all_scraped_data = get_categories(url_site)
    
    #Save data if data was extract
    if all_scraped_data:
        save_to_csv(all_scraped_data)
        print(f"Scraping terminé avec succès. {len(all_scraped_data)} livres récupérés au total.")
    else:
        print("Aucune donnée récupérée. Vérifiez la connexion et l'URL du site.")
    
    print("FIN DU SCRAPING COMPLET")