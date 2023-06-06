import numpy as np
import matplotlib.pyplot as plt

#Constante Globale
c = 299792458 # Vitesse de la lumière dans le vide en m/s
class RadarData:
    def __init__(self,path: str):
        self.path = path
    
    def rd_mat_high_freq(self):
        try:
            if(self.path.endswith(".rd3")):
                with open(self.path, mode='rb') as rd3data:  # Ouvrir le fichier en mode binaire
                    byte_data = rd3data.read()
                rd3 = np.frombuffer(byte_data, dtype=np.int16) #rd3 est codé sur 2 octets
                rd3 = rd3.reshape(self.get_rad()[0], self.get_rad()[1])
                print("Taille du tableau :", rd3.shape)
                return rd3
            elif(self.path.endswith(".rd7")):
                with open(self.path, mode='rb') as rd7data:  # Ouvrir le fichier en mode binaire
                    byte_data = rd7data.read()
                rd7 = np.frombuffer(byte_data, dtype=np.int32)
                rd7 = rd7.reshape(self.get_rad()[0], self.get_rad()[1]) # rd7 est codé sur 3 octets
                print("Taille du tableau :", rd7.shape)
                return rd7
        except Exception as e:
            print("Erreur lors de la lecture du fichier:", str(e))

        
    def get_rad(self):
        rad_file_path = self.path[:-2]+"ad"

        # Lecture du fichier .rad
        with open(rad_file_path, 'r') as file:
            lines = file.readlines()

        # Traitement des lignes du fichier
        for line in lines:
            line = line.strip()  # Supprimer les espaces en début et fin de ligne
            if "SAMPLES" in line:
                value = line.split(':')[1]
                value_sample = int(value)
            elif "LAST TRACE" in line:
                value = line.split(':')[1]
                value_trace = int(value)
                break # on arrête la boucle car nous avons trouvé les deux variables souhaités
        return value_sample, value_trace
        



path_rd3_high = "/home/cytech/Stage/Mesures/JOUANY1/JOUANY1_0001_1.rd7"
radardata = RadarData(path_rd3_high)
radardata.rd_mat_high_freq()
        

