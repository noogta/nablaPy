from RadarData import RadarData
import numpy as np
import matplotlib.pyplot as plt
import cv2
class RadarController():
    def __init__(self,path):
        self.data = RadarData(path)
        self.rd = self.data.rd_mat()
    
    def static_gain(self, g: float,rd: np.ndarray):
        rd = rd.astype(np.float32)
        rd = rd*g
        rd= np.clip(rd, -65535, 65535)
        rd = rd.astype(np.uint16)
        return rd
    
    def apply_linear_gain(self,image, gain, start_line):
        """
        Applique un gain linéaire à une image codée sur 2 octets à partir d'une ligne spécifiée.
        
        Args:
            image (numpy.ndarray): L'image d'entrée sous forme de tableau NumPy codé sur 2 octets.
            gain (float): Le facteur de gain linéaire à appliquer.
            start_line (int): La ligne à partir de laquelle le gain doit être appliqué. Par défaut, 0.
        
        Returns:
            numpy.ndarray: L'image modifiée avec le gain appliqué à partir de la ligne spécifiée.
        """
        # Conversion de l'image en flottant pour effectuer les calculs
        image_float = image.astype(np.float32)
        samples = image_float.shape[0]
        # Application du gain linéaire
        for i in range(start_line, samples):
            gain = gain + i - start_line + 1
            image_float[i] = np.clip(image_float[i] * gain, -65535, 65535)
        
        # Limitation des valeurs aux bornes de 16 bits
        image_float = np.clip(image_float, -65535, 65535)
        
        # Conversion de l'image en type de données codé sur 2 octets
        image_uint16 = image_float.astype(np.uint16)
        
        return image_uint16

    def gainexp(self, a, t0, image):
        # Conversion de l'image en flottant pour effectuer les calculs
        image_float = image.astype(np.float32)
        samples = image_float.shape[0]
        for i in range(t0, samples):
            # Voir fichier pdf pour voir/comprendre la définition de la fonction du gain exponentielle
            if(t0 ==0):
                if(a ==0):
                    gain = 1
                else:
                    # Prolongement du gain exponentielle par continuité par morceaux
                    gain = -1
            else:
                if(a==0):
                    # 
                    gain = 1
                else:
                    b = -np.log(a)/t0
                    gain = a*np.exp(b*i)-1
            image_float[i] = np.clip(image_float[i] * gain, -65535, 65535)

        # Limitation des valeurs aux bornes de 16 bits
        image_float = np.clip(image_float, -65535, 65535)
        
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
rd_linear = test.apply_linear_gain(rd, 500,0)
rd_static = test.static_gain(85,rd)
rd_exp = test.gainexp(14565,0,rd)

# Affichage de la première image
plt.imshow(rd_exp, cmap="Greys")
# Affichage de la figure
plt.show()
np.save("/home/cytech/Videos/rd_f.npy",rd_linear)