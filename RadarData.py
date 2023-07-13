import numpy as np
import traceback
import readgssi.readgssi as dzt
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
    
    def rd_img(self, path: str):
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
                rd3 = rd3.reshape(self.get_feature(path)[0], self.get_feature(path)[1]) 
                rd3 = rd3.transpose()
                return rd3
            
            elif(path.endswith(".rd7")):
                # Ouvrir le fichier en mode binaire "rb"
                with open(path, mode='rb') as rd7data:  
                    byte_data = rd7data.read()
                    # rd7 est codé 4 octets
                rd7 = np.frombuffer(byte_data, dtype=np.int32)
                # Reshape de rd7
                rd7 = rd7.reshape(self.get_feature(path)[0], self.get_feature(path)[1])
                rd7 = rd7.transpose()
                return rd7
            
            elif(path.endswith(".DZT")):
                # Ouvrir le fichier en mode binaire
                with open(path, mode='rb') as DZTdata:
                    byte_data = DZTdata.read()
                    # DZT est codé 4 octets
                DZT = np.frombuffer(byte_data, dtype=np.int32)[(2**15):,]
                # Reshape de rd7
                DZT = DZT.reshape(self.get_feature(path)[0], self.get_feature(path)[1])
                DZT = DZT.transpose()
                return DZT
            
            # À supprimer
            #README
            # Si vous souhaitez rajouter d'autres format:
            # -1 Ajouter elif(path.endswith(".votre_format")):
            # -2 Veuillez vous renseigner sur la nature de vos données binaire, héxadécimal ...
            # -3 Lire les fichiers et ensuite les transférer dans un tableau numpy
            # -4 Redimmensionnez votre tableau à l'aide du nombre de samples et de traces
            # -5 Transposez le tableau

        except:
            print("Erreur lors de la lecture du fichier:")
            traceback.print_exc()

    def get_feature(self, path: str):
        """
    Méthode permettant de récupérer les données contenues dans le fichier .rad.

    Return:
        Retourne les informations suivantes (dans cet ordre):\n
            - trace (int) : nombre de mesures\n
            - samples (int): nombre d'échantillons\n
            - distance total (float): distance totale\n
            - time (float): Temps d'aller\n
            - step (float): distance par mesure (horizontal (sol))\n
            - stem time (float): temps par mesure (horizontal (sol))
        """
        value_trace = None
        value_sample = None
        value_dist_total = None
        value_time = None
        value_step = None
        value_step_time_acq = None
        try:
            if(path.endswith(".rd3") or path.endswith(".rd7")):
                rad_file_path = path[:-2]+"ad"

                # Lecture du fichier .rad
                with open(rad_file_path, 'r') as file:
                    lines = file.readlines()

                # Traitement des lignes du fichier
                for line in lines:
                    # Supprimer les espaces en début et fin de ligne
                    line = line.strip()
                    if "SAMPLES" in line:
                        value = line.split(':')[1]
                        value_sample = int(value)
                    elif "LAST TRACE" in line:
                        value = line.split(':')[1]
                        value_trace = int(value)
                    elif "STOP POSITION" in line:
                        value = line.split(':')[1]
                        value_dist_total = float(value)
                    elif "TIMEWINDOW" in line:
                        value = line.split(':')[1]
                        value_time = float(value)
                    elif "DISTANCE INTERVAL" in line:
                        value = line.split(':')[1]
                        value_step = float(value)
                    elif "TIME INTERVAL" in line:
                        value = line.split(':')[1]
                        value_step_time_acq = float(value)
                    elif "ANTENNAS" in line:
                        value = line.split(':')[1]
                        value_antenna = value           
                return value_trace, value_sample, value_dist_total, value_time,  value_step, value_step_time_acq, value_antenna
            else:
                if(path.endswith(".DZT")):
                    hdr = dzt.readgssi(infile=path, zero=[0])[0]
                    value_trace = hdr['shape'][1]
                    value_sample = hdr['shape'][0]
                    value_dist_total = value_trace / hdr['dzt_spm']
                    value_time = hdr['rhf_range']
                    value_step = hdr['dzt_spm']
                    value_step_time_acq = hdr['dzt_sps']
                    value_antenna = hdr['rh_antname'][0]
                return value_trace, value_sample, value_dist_total, value_time,  value_step, value_step_time_acq, value_antenna
        except:
            print("Erreur lors de la lecture des données:")
            traceback.print_exc()