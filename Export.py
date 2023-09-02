import json
import os
from PIL import Image
import numpy as np

class ExJsonNone:
    """
    Cette classe permet d'exporter des images avec leur classe (ici "None" pour "Aucun").
    """
    def __init__(self, img, file_name):
        """
        Constructeur de la classe ExJsonNone.

        Args:
            - img: tableau de type numpy array
            - file_name: nom du fichier
        """
        self.img = img
        self.file_name = file_name
        data = self.data()
        self.save_data(data)

    def data(self):
        """
        Cette méthode permet de récupérer les données et de les placer dans un dictionnaire.
        """
        new_data = {
            "image": self.file_name, 
            "label": None
        }
        return new_data

    def save_data(self, new_data):
        """
        Cette méthode permet de sauvegarder les données dans un fichier json avec l'image.

        Args:
            - new_data: données à sauvegarder
        """
        current_script_path = os.path.abspath(__file__)
        dir = os.path.dirname(current_script_path)
        json_filename = dir+"/dataset/"+str(self.file_name)+".json"

        # Vérifie si le fichier JSON existe déjà
        if os.path.exists(json_filename):
            # Charge les données existantes depuis le fichier
            with open(json_filename, "r") as json_file:
                existing_data = json.load(json_file)
            # Ajoute les nouvelles données à la liste existante
            existing_data.append(new_data)
        else:
            # Si le fichier n'existe pas, créer une nouvelle liste avec les nouvelles données
            existing_data = [new_data]
        
        # Écris les données mises à jour dans le fichier JSON
        with open(json_filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

        print("Données ajoutées avec succès au fichier JSON.")

        self.img = (self.img - self.img.min()) / (self.img.max() - self.img.min())  # Normalisation
        self.img = (self.img * 255).astype(np.uint8)  # Conversion en uint8

        image_pil = Image.fromarray(self.img)
        image_pil.save(dir+"/dataset/"+str(self.file_name)+".png")
        print("Données ajoutées avec succès au fichier JSON.")

class ExJsonPoint:
    """
    Cette classe permet d'exporter des images avec leur classe et la forme point.
    """
    def __init__(self, img, file_name, label, x, y):
        """
        Constructeur de la classe ExJsonNone.

        Args:
            - img: tableau de type numpy array
            - file_name: nom du fichier
            - label: classe de la forme
            - x: coordonnées en abscisse
            - y: coordonnées en ordonnée
        """
        self.img = img
        self.file_name = file_name
        self.label = label
        self.x = x
        self.y = y
        data = self.data()
        self.save_data(data)

    def data(self):
        """
        Cette méthode permet de récupérer les données et de les placer dans un dictionnaire.
        """
        new_data = {
            "image": self.file_name, 
            "label": self.label,
            "coordinates": {
                "x": self.x,
                "y": self.y,
            }  
        }
        return new_data

    def save_data(self, new_data):
        current_script_path = os.path.abspath(__file__)
        dir = os.path.dirname(current_script_path)
        json_filename = dir+"/dataset/"+str(self.file_name)+".json"
        
        # Vérifie si le fichier JSON existe déjà
        if os.path.exists(json_filename):
            # Charge les données existantes depuis le fichier
            with open(json_filename, "r") as json_file:
                existing_data = json.load(json_file)
            
            # Ajoute les nouvelles données à la liste existante
            existing_data.append(new_data)
        else:
            # Si le fichier n'existe pas, créer une nouvelle liste avec les nouvelles données
            existing_data = [new_data]

        # Écris les données mises à jour dans le fichier JSON
        with open(json_filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

        print("Données ajoutées avec succès au fichier JSON.")

        self.img = (self.img - self.img.min()) / (self.img.max() - self.img.min())  # Normalisation
        self.img = (self.img * 255).astype(np.uint8)  # Conversion en uint8

        image_pil = Image.fromarray(self.img)
        image_pil.save(dir+"/dataset/"+str(self.file_name)+".png")
        print("Données ajoutées avec succès au fichier JSON.")

class ExJsonRectangle:
    """
    Cette classe permet d'exporter des images avec leur classe et la forme rectangle.
    """
    def __init__(self, img, file_name, label, x1, y1, x2, y2):
        """
        Constructeur de la classe ExJsonNone.

        Args:
            - img: tableau de type numpy array
            - file_name: nom du fichier
            - label: classe de la forme
            - x1: coordonnées en abscisse minimal
            - y1: coordonnées en ordonnée minimal
            - x2: coordonnées en abscisse maximal
            - y2: coordonnées en ordonnée maximal
        """
        self.img = img
        self.file_name = file_name            
        self.label = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        data = self.data()
        self.save_data(data)

    def data(self):
        """
        Cette méthode permet de récupérer les données et de les placer dans un dictionnaire.
        """
        new_data = {
            "image": self.file_name, 
            "label": self.label,
            "coordinates": {
                "x1": self.x1,
                "y1": self.y1,
                "x2": self.x2,
                "y2": self.y2
            }  
        }
        return new_data

    def save_data(self, new_data):
        """
        Cette méthode permet de sauvegarder les données dans un fichier json avec l'image.

        Args:
            - new_data: données à sauvegarder
        """
        current_script_path = os.path.abspath(__file__)
        dir = os.path.dirname(current_script_path)
        json_filename = dir+"/dataset/"+str(self.file_name)+".json"

        # Vérifie si le fichier JSON existe déjà
        if os.path.exists(json_filename):
            # Charger les données existantes depuis le fichier
            with open(json_filename, "r") as json_file:
                existing_data = json.load(json_file)
            
            # Ajoute les nouvelles données à la liste existante
            existing_data.append(new_data)
        else:
            # Si le fichier n'existe pas, créer une nouvelle liste avec les nouvelles données
            existing_data = [new_data]

        # Écris les données mises à jour dans le fichier JSON
        with open(json_filename, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

        print("Données ajoutées avec succès au fichier JSON.")

        self.img = (self.img - self.img.min()) / (self.img.max() - self.img.min())  # Normalisation
        self.img = (self.img * 255).astype(np.uint8)  # Conversion en uint8

        image_pil = Image.fromarray(self.img)
        image_pil.save(dir+"/dataset/"+str(self.file_name)+".png")
        print("Données ajoutées avec succès au fichier JSON.")