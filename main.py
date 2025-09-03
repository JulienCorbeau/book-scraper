# Importations
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv

# Définition des fonctions
#Récupération des catégories
def get_categories(url_site):
    categories  = {}
    response = requests.get(url_site)
    if (response.status_code == 200 ) :
        soup = BeautifulSoup(response.text, 'html.parser')
        bloc_category = soup.find('div', class_="side_categories")
        ul_elements = bloc_category.find('ul', class_='nav nav-list')
        url_cat = ul_elements.find_all('a')

        for lien in url_cat:
            categorie_name = lien.text.strip()
            categorie_url = lien['href']
            full_url = "http://books.toscrape.com/" + categorie_url
            categories[categorie_name] = full_url
        #categories['travel'] = {'nom':'travel', 'url':'http://test.php'}
    else:
        print(f"Erreur de requête: Le code de statut est {response.status_code}")
    return categories
#    pass    

#Récupération des URLs des livres dans une catégorie
def get_pages_from_category(url):
    requete = requests.get(url)
    if (requete.status_code == 200): 
        #Récupération du nombre de pages dans cette categorie
        liste_url_book = []   
        soup = BeautifulSoup(requete.text, 'html.parser')
        #presencePageFoot = soup.find()
        if soup.find('ul', class_="pager") :
            pageFoot = soup.find('ul', class_="pager")
            string_temp = pageFoot.text
            string_temp = string_temp.split("next")[0].strip()
            nbPageCategorie = int(string_temp[-1])
            #nbPageCategorie = int(nbPageCategorie)
        else : 
            nbPageCategorie = 1
        liste_url_book.append(url) 
        if nbPageCategorie > 1 :
            for i in range(nbPageCategorie-1) :
                pageTemp = "page-" + str(i+2) + ".html"
                urlTemp = url.replace("index.html", pageTemp)
                liste_url_book.append(urlTemp)
    else :
        print(f"Message d'erreur : {requete.status_code}")
    return(liste_url_book)            

def get_url_from_page(url_page):
    requete = requests.get(url_page)
    liste_url_books = [] # Initialize the list here

    if (requete.status_code == 200):
        soup = BeautifulSoup(requete.text, 'html.parser')
        structure = soup.find('ol', class_='row')
        
        if structure: # Added this check for robustness
            all_books = structure.find_all('li')
            for book in all_books:
                link_book = book.find('a')
                if link_book:
                    relative_url = link_book['href']
                    # Correct way to build the full URL
                    # The ../../../ part needs to be removed
                    full_url = "http://books.toscrape.com/catalogue/" + relative_url.replace('../', '')
                    liste_url_books.append(full_url)
    else:
        print(f"Message d'erreur : {requete.status_code}")
    
    return liste_url_books
    

#Extraction des données d'un livre
def scrape_book_data(url):
    response = requests.get(url)

    # Vérifiez que la requête a réussi (statut 200)
    if response.status_code == 200:
        # --- Étape 2: Analyser le contenu HTML avec BeautifulSoup ---
        livre_temp = {}
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Étape 3: Extraire les informations du livre ---
        title_element = soup.find('h1')
        livre_temp['titre'] = title_element.text
        
        prix_element = soup.find('p', class_='price_color')
        livre_temp['prix']= prix_element.text.replace('£', '')
        return livre_temp
    else:
        print(f"Erreur de requête: Le code de statut est {response.status_code}")



#Enregistrement des données dans un fichier CSV
def save_to_csv(categorie, books_cat): 
    #Créer et enregistrer les données dans un fichier CSV ---
    # Assurez-vous que les dossiers de sortie existent
    Path("data/csv").mkdir(parents=True, exist_ok=True)

    # Définir le nom du fichier de sortie
    nom_fichier = 'data/csv/Scraping_'+categorie+'.csv'

    # Écrire les données dans le fichier CSV
    with open(nom_fichier, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
            
        # En-têtes de colonne
        writer.writerow(['Titre', 'Prix'])
            
        # Données du livre
        for book in books_cat :
            writer.writerow([book['titre'], book['prix']])

    print(f"Les données ont été extraites et sauvegardées dans {nom_fichier}")



# Vérifie que le script est le programme principal
if __name__ == "__main__":
    #Définition du site à extraire
    url_site = "https://books.toscrape.com/"
    #Récupération des différentes catégories
    categories = get_categories(url_site)
    #Définition manuelle d'une catégorie pour la partie 3
    #categorie = 'Travel'
    #url_categorie = categories['Travel']
    
    #Boucle sur toutes les catégories prélevé par la fonction get
    for categorie in categories:
        compt = 0   # Compteur pour vérifier qu'on récupère tous les livres d'une catégorie en prenant en compte s'il y a plusieurs pages
        books_cat = []
        #Récupération des liens url des différentes pages d'une catégorie
        url_categorie = categories[categorie]
        liste_url_pages = get_pages_from_category(url_categorie)
        #Boucle pour parcourir les pages
        for url_page in liste_url_pages:
            liste_url_books = get_url_from_page(url_page)
            #Boucle pour récupérer les liens url des livres d'une page et les stocker dans un dictionnaire
            for url_book in liste_url_books :
                compt = compt + 1
                livre_temp = scrape_book_data(url_book)
                books_cat.append(livre_temp) #stockage du dictionnaire livre dans la liste books_cat
        print(f"Il y a eu {str(compt)} références récupérées dans la catégories : {categorie}")
        save_to_csv(categorie, books_cat)

    #print(liste_url_book)
    #livre_temp = scrape_book_data(url)
    #for nom_categorie, url_categorie in categories.items():
    #    print(f"{nom_categorie} : {url_categorie}")
    #save_to_csv(data=None, filename=None, livre_temp=livre_temp)