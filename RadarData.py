import numpy as np
import matplotlib.pyplot as plt
import os

#Constante Globale Dictionnaire
cste_global = {
    "c_lum": 299792458, # Vitesse de la lumière dans le vide en m/s
    }

class RadarData:
    """RadarData: Classe contenant toutes les méthodes permettant d'avoir accès aux différentes données"""
    def __init__(self):
        """
    Constructeur de la classe RadarData.

    Args:
        """
    
    def rd_mat(self, path: str):
        """
    Méthode permettant de récupérer la zone sondée à partir d'un fichier .rd3 ou .rd7.

    Return:
        Retourne le tableau numpy contenant les données de la zone sondée.
        """
        try:
            if(path.endswith(".rd3")):
                # Ouvrir le fichier en mode binaire "rb"
                with open(path, mode='rb') as rd3data:  
                    byte_data = rd3data.read()
                # rd3 est codé sur 2 octets
                rd3 = np.frombuffer(byte_data, dtype=np.int16) 
                # Reshape de rd3
                rd3 = rd3.reshape(self.get_rad(path)[0], self.get_rad(path)[1]) 
                rd3 = rd3.transpose()
                #print("Taille du tableau :", rd3.shape)
                return rd3
            elif(path.endswith(".rd7")):
                # Ouvrir le fichier en mode binaire "rb"
                with open(path, mode='rb') as rd7data:  
                    byte_data = rd7data.read()
                    # rd7 est codé sur 3 octets
                rd7 = np.frombuffer(byte_data, dtype=np.int32)
                # Reshape de rd7
                rd7 = rd7.reshape(self.get_rad(path)[0], self.get_rad(path)[1]) 
                rd7 = rd7.transpose()
                #print("Taille du tableau :", rd7.shape)
                return rd7
            
            #README
            # Si vous souhaitez rajouter d'autres format:
            # -1 Ajouter elif(path.endswith(".votre_format")):
            # -2 Veuillez vous renseigner sur la nature de vos données binaire, héxadécimal ...
            # -3 Lire les fichiers et ensuite les transférer dans un tableau numpy
            # -4 Redimmensionnez votre tableau à l'aide du nombre de samples et de traces
            # -5 Transposez le tableau

        except Exception as e:
            print("Erreur lors de la lecture du fichier.\nVérifier que l'extension de votre fichier soit lisible.\n Pour cela:\n Modifier --> Afficher les extensions\n\n\n\n", str(e))

    def get_rad(self, path: str):
        """
    Méthode permettant de récupérer les données contenues dans le fichier .rad.

    Return:
        Retourne le tableau numpy contenant les données de la zone sondée.
        """
        rad_file_path = path[:-2]+"ad"

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
    
    def add_list_extension(self, ext: str):
        path = os.path.dirname(__file__)
        with open(path+"/data/ext.txt", 'a') as file:
            file.write("\n"+ext)

    def get_list_extension(self):
        path = os.path.dirname(__file__)
        with open(path+"/data/ext.txt", 'r') as file:
            f = (file.read())
        elements = f.split("\n")
        return elements

    def delete_list_extension(self, ext_del: str):
        path = os.path.dirname(__file__)
        list_ext = self.get_list_extension()
        if ext_del in list_ext:
            list_ext.remove(ext_del)
            # Ouvrir le fichier en mode écriture et écrire le contenu mis à jour
            with open(path+"/data/ext.txt", "w") as file:
                for i in range(len(list_ext)):
                    file.write(list_ext[i]+"\n")
        else:
            print(f"{ext_del} n'est pas présent dans le fichier.")
"""
path = "/home/cytech/JOUANY1/JOUANY1_0001_1.rd3"
test = RadarData()
rd = test.rd_mat(path)
print(rd)
plt.imshow(rd, cmap="Greys")
plt.show()
"""
