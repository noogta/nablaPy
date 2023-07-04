from RadarData import RadarData
import numpy as np
import traceback

class RadarController():
    def __init__(self):
        return

    def apply_constant_gain(self, img:np.ndarray, gain: float):
        """
        Applique un gain constant à une image.

        Args:
            img (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy.
            gain (float): Le facteur de gain constant à appliquer.

        Returns:
            numpy.ndarray: L'image modifiée avec le gain constant appliqué.
        """
        # Conversion de l'image en flottant pour effectuer les calculs
        bit = self.get_bit_img(img)
        # Conversion de notre matrice/image en float
        img = img.astype("float"+str(bit))
        # Application du gain constant
        img = np.clip(img * gain, -(2**bit)+1, (2**bit)-1)
        return img

    def apply_linear_gain(self, img: np.ndarray, t0: int, gain: float):
        """
        Applique un gain linéaire croissant à une image à partir d'une ligne spécifiée.

        Args:
            img (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy.
            t0 (int): La ligne à partir de laquelle le gain doit être appliqué.
            gain (float): Le facteur de gain linéaire initial.

        Returns:
            numpy.ndarray: L'image modifiée avec le gain linéaire croissant appliqué à partir de la ligne spécifiée.
        """
        bit = self.get_bit_img(img)
        # Conversion de notre matrice/image en float
        img = img.astype("float"+str(bit))
        height = img.shape[0]

        for i in range(t0, height):
            current_gain = gain * (i - t0)+1
            img[i] = np.clip(img[i] * current_gain, -(2**bit) +1, (2**bit)+1)

        img = np.clip(img, -(2**bit)+1,(2**bit)-1)
        return img

    # en construction
    def apply_exponentiel_gain(self, img: np.ndarray, t0: int, a: float):
        # Conversion de l'image en flottant pour effectuer les calculs
        bit = self.get_bit_img(img)
        image_float = img.astype("float"+str(bit))
        samples = image_float.shape[0]
        fgain = np.ones(samples)
        L = np.arange(samples)
        fgain[t0:] = np.exp(a * (L[t0:] - t0))
        image_float = image_float * fgain[:, np.newaxis]
        image_float = np.clip(image_float, -(2**bit)+1, (2**bit)-1)
        return image_float

    def apply_total_gain(self, img: np.ndarray, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float):
        """
    Méthode permettant d'appliquer le gain souhaité à l'image.
    Afin de comprendre la construction des fonctions gains (cf Doc/NablaPy.pdf)

    Args:
            t0 (float): La ligne à partir de laquelle le gain doit être appliqué.
            g (float): Coefficient du gain normal
            a_lin (float): Coefficient du gain linéaire (Fonction linéaire f:x --> a(x-t0)
            a (float): Coefficient d'atténuation de l'exponentielle (Fonction exponentielle: f: x --> exp(a(x-t0)))

    Returns:
            ndarray : Retourne le tableau traité.
        """
                # Conversion de l'image en flottant pour effectuer les calculs
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
        
        #fgain[t0:] = np.exp(a * (L[t0:] - t0))+g*L[t0:]+a_lin*(L[t0:]-t0) #t0 indépendant

        # Gain constant
        fgain *= g
        # Gain linéaire
        fgain[t0_lin:] += a_lin*(L[t0_lin:]-t0_lin)

        # Gain exponentiel
        fgain[t0_exp:] +=  np.exp(a * (L[t0_exp:] - t0_exp))
        image_float = image_float * fgain[:, np.newaxis]
        
        image_float = np.clip(image_float, -(2**bits)+1, (2**bits)-1, dtype=image_float.dtype)
        return image_float
    
    
    def get_bit_img(self, img: np.ndarray):
        """
        Récupère le nombre de bits à partir d'un tableau (néccessaire pour les fonctions gain).

        Args:
            img (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy.

        Returns:
            int: Le nombre de bits du format.
        """
        format = img.dtype.name
        if format.startswith("float"):
            return int(format[5:])
        elif format.startswith("int"):
            return int(format[3:])
        else:
            raise ValueError("Format invalide. Votre tableau numpy est d'un type différent de celui-ci:\n- int\n- float")
        
    def dewow_filter(self, array: np.ndarray):
        """
        Applique le filtre dewow à un tableau de données.

        Arguments:
            - data: Le tableau de données d'entrée.
            - window_size: La taille de la fenêtre de filtrage (par défaut: 5).

        Retourne:
            - Le tableau de données filtré.
        """
        try:
            # Calculer la moyenne par colonne
            col_mean = np.mean(array, axis=0)
            # Soustraire la moyenne de chaque colonne au tableau d'entrée
            dewowed_arr = array - col_mean
            return dewowed_arr
        except:
            print("Le paramètre en entrée n'est ni un vecteur ni une matrice:")
            traceback.print_exc()

