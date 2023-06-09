import numpy as np
import matplotlib.pyplot as plt
import os
#Constante Globale Dictionnaire
cste_global = {
    "c_lum": 299792458, # Vitesse de la lumière dans le vide en m/s
    }

class RadarData:
    """RadarData: Classe contenant toutes les méthodes permettant avoir accès aux différentes données"""
    def __init__(self,path: str):
        """
    Constructeur de la classe RadarData.

    Args:
                path (str): chemin du fichier
        """
        self.path = path
    
    def rd_mat(self):
        """
    Méthode permettant de récupérer la zone sondée à partir d'un fichier .rd3 ou .rd7.

    Return:
        Retourne le tableau numpy contenant les données de la zone sondée.
        """
        try:
            if(self.path.endswith(".rd3")):
                # Ouvrir le fichier en mode binaire "rb"
                with open(self.path, mode='rb') as rd3data:  
                    byte_data = rd3data.read()
                # rd3 est codé sur 2 octets
                rd3 = np.frombuffer(byte_data, dtype=np.int16) 
                # Reshape de rd3
                rd3 = rd3.reshape(self.get_rad()[0], self.get_rad()[1]) 
                rd3 = rd3.transpose()
                #print("Taille du tableau :", rd3.shape)
                return rd3
            elif(self.path.endswith(".rd7")):
                # Ouvrir le fichier en mode binaire "rb"
                with open(self.path, mode='rb') as rd7data:  
                    byte_data = rd7data.read()
                    # rd7 est codé sur 3 octets
                rd7 = np.frombuffer(byte_data, dtype=np.int32)
                # Reshape de rd7
                rd7 = rd7.reshape(self.get_rad()[0], self.get_rad()[1]) 
                rd7 = rd7.transpose()
                #print("Taille du tableau :", rd7.shape)
                return rd7
            
            #README
            # Si vous souhaitez rajouter d'autres format:
            # -1 Ajouter elif(self.path.endswith(".votre_format")):
            # -2 Veuillez vous renseigner sur la nature de vos données binaire, héxadécimal ...
            # -3 Lire les fichiers et ensuite les transférer dans un tableau numpy
            # -4 Redimmensionnez votre tableau à l'aide du nombre de samples et de traces
            # -5 Transposez le tableau

        except Exception as e:
            print("Erreur lors de la lecture du fichier:", str(e))
            return e

    def get_rad(self):
        """
    Méthode permettant de récupérer les données contenues dans le fichier .rad.

    Return:
        Retourne le tableau numpy contenant les données de la zone sondée.
        """
        rad_file_path = self.path[:-2]+"ad"

        # Lecture du fichier .rad
        with open(rad_file_path, 'r') as file:
            lines = file.readlines()

        # Traitement des lignes du fichier
        for line in lines:
            line = line.strip()
            # Supprimer les espaces en début et fin de ligne
            if "SAMPLES" in line:
                value = line.split(':')[1]
                value_sample = int(value)
            elif "LAST TRACE" in line:
                value = line.split(':')[1]
                value_trace = int(value)
                # Arrêt la boucle car nous avons trouvé les deux variables souhaités
                break 
        return value_trace, value_sample
    
path_rd3_high = "/home/cytech/Stage/Mesures/JOUANY1/JOUANY1_0001_1.rd3"

test = RadarData(path_rd3_high)
test.rd_mat()