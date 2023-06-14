from RadarData import RadarData
import numpy as np
import matplotlib.pyplot as plt

import re
class RadarController():
    def __init__(self, data: RadarData):
        self.data = data

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
        bit = self.get_bit_img(img)
        image_float = img.astype("float"+str(bit))
        samples = image_float.shape[0]
        fgain = np.zeros(samples)
        L = np.arange(samples)

        #fgain[t0:] = np.exp(a * (L[t0:] - t0))+g*L[t0:]+a_lin*(L[t0:]-t0) #t0 indépendant

        # Gain constant
        fgain *= g

        # Gain linéaire
        fgain[t0_lin:] += a_lin*(L[t0_lin:]-t0_lin)

        # Gain exponentiel
        fgain[t0_exp:] += np.exp(a * (L[t0_exp:] - t0_exp))

        image_float = image_float * fgain[:, np.newaxis]
        
        image_float = np.clip(image_float, -(2**bit)+1, (2**bit)-1)
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

"""data = RadarData()
test = RadarController(data)
rd = data.rd_mat("/home/cytech/JOUANY1/JOUANY1_0001_1.rd3")
rd = test.apply_total_gain(rd,0,0,7.,4.,0.)
plt.imshow(rd, cmap="Greys")
plt.show()"""