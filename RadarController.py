from RadarData import RadarData
import numpy as np
import matplotlib.pyplot as plt
class RadarController():
    def __init__(self,path):
        self.data = RadarData(path)
        self.path = path
    
    def static_gain(self,g: float):
        """
    Méthode permettant d'appliquer un gain statique à une image.

    Args:
            g (float): gain

    Return:
            Retourne le tableau traité.
        """
        rd = self.data.rd_mat()
        rd = rd * g
        print(rd.shape)
        return rd

    def linear_gain(self, a: float, b: float):
        """
    Méthode permettant d'appliquer un gain linéaire à une image.

    Args:
            a (float): coefficient
            b (float): l'ordonnée à l'origine
            (Fonction linéaire f:x --> ax+b)

    Return:
            Retourne le tableau traité.
        """
        rd = self.data.rd_mat()
        rd = (rd * a) + b
        return rd
    
    def exp_gain(self, a: float, b: float):
        """
    Méthode permettant d'appliquer un gain linéaire à une image.

    Args:
            a (float): coefficient
            b (float): l'ordonnée à l'origine
            (Fonction linéaire f:x --> ax+b)

    Return:
            Retourne le tableau traité.

        """
        rd = self.data.rd_mat()
        rd = rd # en construction
        print(rd.shape)
        return rd
    



path_rd3_high = "/home/cytech/Stage/Mesures/JOUANY1/JOUANY1_0001_1.rd3"
test = RadarController(path_rd3_high)
rd = test.exp_gain(8,9)
plt.imshow(rd,)
plt.show()