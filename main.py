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
def get_urls_from_category(url):
    #Récupération du nombre de page dans cette categorie
    requete = requests.get(url)
    if (requete.status_code == 200): 
        liste_url_book = []   
        soup = BeautifulSoup(requete.text, 'html.parser')
        presencePageFoot = soup.find()
        if soup.find('ul', class_="pager") :
            pageFoot = soup.find('ul', class_="pager")
            string_temp = pageFoot.text
            string_temp = string_temp.split("next")[0].strip()
            nbPageCategorie = string_temp[-1]
            nbPageCategorie = int(nbPageCategorie)
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
    else:
        print(f"Erreur de requête: Le code de statut est {response.status_code}")
    return livre_temp


#Enregistrement des données dans un fichier CSV
def save_to_csv(data, filename, livre_temp): 
    #Créer et enregistrer les données dans un fichier CSV ---
    # Assurez-vous que les dossiers de sortie existent
    Path("data/csv").mkdir(parents=True, exist_ok=True)

    # Définir le nom du fichier de sortie
    nom_fichier = 'data/csv/single_book.csv'

    # Écrire les données dans le fichier CSV
    with open(nom_fichier, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
            
        # En-têtes de colonne
        writer.writerow(['Titre', 'Prix'])
            
        # Données du livre
        writer.writerow([livre_temp['titre'], livre_temp['prix']])

    print(f"Les données ont été extraites et sauvegardées dans {nom_fichier}")



# Vérifie que le script est le programme principal
if __name__ == "__main__":
    url_site = "https://books.toscrape.com/"
    categories = get_categories(url_site)
    categorie = 'Nonfiction'
    url_categorie = categories['Nonfiction']
    print(f"'Fiction' : {url_categorie}")
    liste_url_book = get_urls_from_category(url_categorie)
    print(liste_url_book)
    #livre_temp = scrape_book_data(url)
    #for nom_categorie, url_categorie in categories.items():
    #    print(f"{nom_categorie} : {url_categorie}")
    #save_to_csv(data=None, filename=None, livre_temp=livre_temp)