from RadarData import RadarData
import numpy as np
import matplotlib.pyplot as plt
import cv2
class RadarController():
    def __init__(self,path):
        self.data = RadarData(path)
        self.rd = self.data.rd_mat()

    def apply_constant_gain(self,image, gain):
        """
        Applique un gain constant à une image codée sur 2 octets.

        Args:
            image (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy codé sur 2 octets.
            gain (float): Le facteur de gain constant à appliquer.

        Returns:
            numpy.ndarray: L'image modifiée avec le gain constant appliqué.
        """
        # Conversion de l'image en flottant pour effectuer les calculs
        image_float = image.astype(np.float16)

        # Application du gain constant
        image_float = np.clip(image_float * gain, -65535.0, 65535.0)

        return image_float



    def apply_linear_gain(self, image, start_line, gain):
        """
        Applique un gain linéaire croissant à une image codée sur 2 octets à partir d'une ligne spécifiée.

        Args:
            image (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy codé sur 2 octets.
            start_line (int): La ligne à partir de laquelle le gain doit être appliqué.
            gain (float): Le facteur de gain linéaire initial.

        Returns:
            numpy.ndarray: L'image modifiée avec le gain linéaire croissant appliqué à partir de la ligne spécifiée.
        """
        image_float = image.astype(np.float16)
        height = image_float.shape[0]

        for i in range(start_line, height):
            current_gain = gain + (i - start_line)+1
            image_float[i] = np.clip(image_float[i] * current_gain, -65535.0, 65535.0)

        image_float = np.clip(image_float, -65535, 65535)
        return image_float


    def gainexp(self, a, t0, image):
        # Conversion de l'image en flottant pour effectuer les calculs
        image_float = image.astype(np.float32)
        samples = image_float.shape[0]
        """
        for i in range(t0, samples):
            # Voir fichier pdf pour voir/comprendre la définition de la fonction du gain exponentielle
            if(t0 ==0):
                gain = 0
            else:
                if(a==0):
                    # 
                    gain = 0
                else:
                    b = -np.log(a)/t0
                    gain = a*np.exp(b*i)
            if(gain !=0):
                image_float[i] = np.clip(image_float[i] * gain, 0, 65535)
        """
        # Limitation des valeurs aux bornes de 16 bits
        image_float = np.clip(image_float, 0, 65535)
        
        # Conversion de l'image en type de données codé sur 2 octets
        image_uint16 = image_float.astype(np.uint16)
        return image_uint16

    def gain_function(self, g: float, a_lin: float, amp: float, b:float, t0: float):
        """
    Méthode permettant d'appliquer le gain souhaité à l'image.
    Afin de comprendre la construction des fonctions gains (cf Doc/NablaPy.pdf)

    Args:
            g (float): coefficient du gain normal
            a_lin (float): coefficient du gain linéaire (Fonction linéaire f:x --> a(x-t0)+1
            a_exp (float): coefficient d'atténuation de l'exponentielle (Fonction exponentielle: f: x --> exp(a(x-t0))+1)
            t0 (float): variable de positionnement du gain sur l'image

    Returns:
            ndarray : Retourne le tableau traité.
        """
        rd = self.rd
        if not rd.flags.writeable:
            rd = np.copy(rd)
        samples, traces = rd.shape
        fgain = np.ones(samples)
        L = [k for k in range(samples)]
        fgain[t0:] = [a_lin*(x-t0) + amp*np.exp(min(b*(x-t0), 10000)) + g for x in L[t0:]]
        for trace in range(traces):
            rd[:, trace] = rd[:, trace] * fgain
        return rd

#Path
path_rd3_high = "/home/cytech/Stage/Mesures/JOUANY1/JOUANY1_0002_1.rd3"

#Test
test = RadarController(path_rd3_high)
rd = test.rd
rd_linear = test.apply_linear_gain(rd, t0 = 0,gain = 5)
rd_static = test.apply_constant_gain(rd,gain = 5)
#rd_exp = test.gainexp(1,0,rd)

# Affichage de la première image
#plt.imshow(rd_linear,cmap="Greys")
plt.imshow(rd_static,cmap="Greys")
# Affichage de la figure
plt.show()
"""
for i in range(rd_linear.shape[0]):
    for j in range(rd_linear.shape[1]):
        if(rd_linear[i][j]-rd_static[i][j] == 0):
            print(i,j)"""