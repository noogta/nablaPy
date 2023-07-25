import numpy as np
import traceback
from scipy import signal

class RadarController():
    """RadarController: Classe permettant de modifier l'image radar"""
    def __init__(self):
        """
        Constructeur de la classe RadarController.
        """
        return

    def apply_total_gain(self, img: np.ndarray, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float):
        """
        Méthode permettant d'appliquer le gain souhaité à l'image.

        Args:
                t0 (float): La ligne à partir de laquelle le gain doit être appliqué.
                g (float): Coefficient du gain normal
                a_lin (float): Coefficient du gain linéaire (Fonction linéaire f:x --> a(x-t0)
                a (float): Coefficient d'atténuation de l'exponentielle (Fonction exponentielle: f: x --> exp(a(x-t0)))

        Returns:
                ndarray : Retourne le tableau traité.
        """
        # Conversion de l'image en flottant pour effectuer les calculs
        try:
            bits = self.get_bit_img(img)
            image_float = img.astype("float"+str(bits))
            samples = image_float.shape[0]
            fgain = None
            if(bits == 16):
                fgain = np.ones(samples, dtype=np.float16)
            else:
                if(bits == 32):
                    fgain = np.ones(samples, dtype=np.float32)
            L = np.arange(samples)
            
            # Gain constant
            fgain *= g

            # Gain linéaire
            fgain[t0_lin:] += a_lin*(L[t0_lin:]-t0_lin)

            # Gain exponentiel
            fgain[t0_exp:] +=  np.exp(a * (L[t0_exp:] - t0_exp))-1
            image_float = image_float * fgain[:, np.newaxis]
            
            image_float = np.clip(image_float, -(2**bits)+1, (2**bits)-1, dtype=image_float.dtype)
            return image_float
        except:
            print("Erreur lors de l'application des gains:")
            traceback.print_exc()
            return image_float
    
    
    def get_bit_img(self, img: np.ndarray):
        """
        Récupère le nombre de bits à partir d'un tableau (néccessaire pour les fonctions gain).

        Args:
            img (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy.

        Returns:
            int: Le nombre de bits du format.
        """
        try:
            format = img.dtype.name
            if format.startswith("float"):
                return int(format[5:])
            else:
                if(format.startswith("int")):
                    return int(format[3:])
        except:
            print("Erreur lors de la lecture des bits:")
            traceback.print_exc()
        
    def dewow_filter(self, img: np.ndarray):
        """
        Applique le filtre dewow à un tableau de données.

        Arguments:
            - img: Le tableau de données d'entrée.
            - window_size: La taille de la fenêtre de filtrage (par défaut: 5).

        Returns:
            - Tableau de données avec le filtre dewow appliqué.
        """
        try:
            # Calculer la moyenne par colonne
            col_mean = np.mean(img, axis=0)
            # Soustraire la moyenne de chaque colonne au tableau d'entrée
            dewowed_arr = img - col_mean
            return dewowed_arr
        except:
            print("Erreur lors de l'application du filtre dewow:")
            traceback.print_exc()

    def sub_mean(self, img: np.ndarray, j: int):
        try:
            n_tr = img.shape[1]
            if j==0:
                mean_tr = np.mean(img, axis=1)
                for k in range(n_tr):
                    img[:,k] = img[:,k] - mean_tr
            else:
                start = j
                end = n_tr - j
                ls=np.arange(start, end, 1)
                for l in ls:
                    mean_tr = np.mean(img[:, l-j:l+j], axis=1)
                    img[:,int(l)] = img[:,l] - mean_tr
                mean_l = np.mean(img[:, 0:start], axis=1)
                mean_r = np.mean(img[:, end:n_tr], axis=1)
                for l in np.arange(0, start, 1):
                    img[:,int(l)] = img[:,l] - mean_l
                for l in np.arange(end, n_tr, 1):
                    img[:,int(l)] = img[:,l] - mean_r
            return img
        except:
            print("Erreur lors de l'application de la trace moyenne:")
            traceback.print_exc()

    def low_pass(self, img: np.ndarray, cutoff_freq: float, sampling_freq: float):
        try:
            normalized_cutoff = cutoff_freq / (sampling_freq / 2)
            b, a = signal.butter(1, normalized_cutoff, btype='low', analog=False)
            new_array = signal.lfilter(b, a, img)
            return new_array
        except:
            print("Erreur lors de l'application du filtre:")
            traceback.print_exc()
            return img