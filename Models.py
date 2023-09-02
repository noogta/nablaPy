import tensorflow as tf
from keras.utils import img_to_array
import os
from PIL import Image
import numpy as np
import platform

# Suppression des lignes générés par L'initialisation de ternsorflow
my_os = platform.system()
if(my_os == "Linux" or my_os== "Darwin"):
    os.system("clear")
else:
    if(my_os == "Windows"):
        os.system("cls")


class Models:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        
        # Récupération du chemin du dossier
        current_script_path = os.path.abspath(__file__)
        self.dir = os.path.dirname(current_script_path)

    def Classification_model(self):
        # Chargement du modèle
        model = tf.keras.models.load_model(self.dir + "/models/Steels_Detection(NOB).h5")

        # Normalisation
        image = (self.mainwindow.img_modified - self.mainwindow.img_modified.min()) / (self.mainwindow.img_modified.max() - self.mainwindow.img_modified.min())

        # Conversion sur 1 octet (8 bits)
        image = (image * 255).astype(np.uint8)

        # Conversion en image
        image = Image.fromarray(image)

        # Redimension de l'image, suivi d'une conversion en tableau numpy
        image = img_to_array(image.resize((224, 224)))

        # Le vecteur d'entrée du modèle doit correspondre à la dimension (1, 224, 224)
        input_img = np.expand_dims(image, axis=0)
        
        # Prédiction probabilités
        s, ns = model.predict(input_img)[0]
        
        if s > ns:
            self.mainwindow.class_prediction.setText("Prédiction: Présence d'acier")
            self.mainwindow.probability_prediction.setText("Probabilité: " + str(s))
        else:
            self.mainwindow.class_prediction.setText("Prédiction: Aucune présence d'acier")
            self.mainwindow.probability_prediction.setText("Probabilité: " + str(ns))

