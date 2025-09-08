# Importations
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv

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
        img_element = soup.find('img')
        url_relative = img_element['src'].replace('../../','')
        livre_temp['img_lien'] = 'http://books.toscrape.com/' + url_relative
        #Création du nom de fichier
        nom_fichier = livre_temp['titre'].replace(' ', '_').replace(':','')+'.jpg'
        download_image(livre_temp['img_lien'], nom_fichier)
        return livre_temp
    else:
        print(f"Erreur de requête: Le code de statut est {response.status_code}")

#Fonction telechargement des images
def download_image(url, filename): #et catégorie
    # Fait une requête GET pour l'image
    response = requests.get(url)
        
    # Vérifie que la requête a réussi (code 200)
    if response.status_code == 200:
        # Assure-toi que le dossier 'data/images' existe
        Path("data/images").mkdir(parents=True, exist_ok=True)
            
        # Ouvre le fichier en mode binaire 'wb' (write binary)
        with open(filename, 'wb') as file:
            # Écrit le contenu de la réponse dans le fichier
            file.write(response.content)
        print(f"Image téléchargée avec succès dans {filename}")
    else:
        print(f"Erreur lors du téléchargement de l'image. Code de statut: {response.status_code}")


# Vérifie que le script est le programme principal
if __name__ == "__main__":
    url_book = 'http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html'
    livre_temp = scrape_book_data(url_book)
    print(livre_temp)
                