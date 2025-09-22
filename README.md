# book-scraper

&nbsp;

#Projet 1 : Système d'extraction de prix pour Books Online



Ce projet est une application en Python développée pour automatiser la collecte de données sur les livres et les prix associés. Il s'agit d'un système de veille tarifaire capable d'extraire, de transformer et de charger (ETL) des données depuis un site web, Books to Scrape. Le programme génère des fichiers CSV par catégorie de livres et télécharge les images associées.



## Installation et exécution



Suivez les étapes ci-dessous pour installer et exécuter le programme.



### Prérequis

- Python 3.x installé sur votre machine.

- Git installé.

- Un environnement de développement (IDE) comme Visual Studio Code ou PyCharm.



### 1. Cloner le dépôt

Clonez ce dépôt sur votre machine locale via la ligne de commande :



_git clone https://github.com/JulienCorbeau/book-scraper\_



### 2. Configuration de l'environnement virtuel

Naviguez jusqu'au répertoire du projet, créez et activez un environnement virtuel pour isoler les dépendances.Ouvrez le terminal dans le répertoire racine de votre projet et exécutez la commande suivante selon votre système d'exploitation :



- Sur Windows : \_python -m venv venv\_

- Sur macOS/Linux : \_python3 -m venv venv\_



Puis activez l'environnement virtuel :



- Sur Windows : \_.\\venv\\Scripts\\activate\_

- Sur macOS/Linux : \_source venv/bin/activate\_





### 3. Installation des dépendances

Installez toutes les bibliothèques nécessaires à partir du fichier `requirements.txt` :



\_pip install -r requirements.txt\_



### 4. Exécution du script

Une fois l'installation terminée, vous pouvez exécuter le script :



\_python main.py\_



Le programme va alors se connecter au site, extraire les données, télécharger les images et créer les fichiers CSV dans le dossier `data/`.



## Livrables du projet



Le script génère les fichiers suivants dans le dossier `data/` :

- Un sous-dossier `csv/` contenant un fichier `.csv` pour chaque catégorie de livres.

- Un sous-dossier `images/` contenant les images de tous les livres, triées par catégorie dans un dossier distinct.



## Contexte de la mission



Ce projet a été réalisé dans le cadre de ma formation de Développeur d’Application Python. Dans le rôle d'analyste marketing, j'ai développé ce programme pour automatiser la collecte des prix et d'autres informations sur un site web concurrent, Books to Scrape, ce qui permettra à l'équipe de gagner un temps précieux et d'analyser le marché de manière plus efficace.

