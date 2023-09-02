import matplotlib.pyplot as plt
import platform
# Couleur des différentes classes
color = {
    "": "black",
    "Acier": "brown", 
    "Anomalie franche": "red",
    "Anomalie hétérogène": "green",
    "Réseaux": "blue", 
    "Autres": "purple"
}

class Point:
    """
    Cette classe permet de tracer des points.
    """
    def __init__(self, label: str, x: float, y: float, rel: float):
        """
        Constructeur de la classe point.
        
        Args:
            - label: classe du point
            - x: coordonnée abscisse
            - y: coordonnée ordonnée
            - rel: rapport entre le minimum et le maximum (abscisse et ordonée)
        """
        self.label = label
        self.x = x
        self.y = y
        self.create_point(relation=rel)
    
    def create_point(self, relation: float):
        """
        Cette méthode crée un point.

        Args:
            - relation: rapport entre le minimum et le maximum (abscisse et ordonée)
        """
        if(self.label == ""):
            self.point = plt.Circle((self.x, self.y), radius=relation, color = color[self.label], alpha = 1)
        else:
            if(self.label in color):
                self.point = plt.Circle((self.x, self.y), radius=relation, color=color[self.label], alpha = 1)

    def update_point(self, x: float, y: float):
        """
        Cette méthode met à jour les coordonnées du point.

        Args:
            - x: coordonnée abscisse
            - y: coordonnée ordonnée
        """
        # Mise à jour des coordonnées
        self.x = x
        self.y = y
        self.point.center = (self.x, self.y)

    def plot(self, axes):
        """
        Cette méthode affiche sur le canvas le point.

        Args:
            - axes: Axes de la figure
        """
        axes.add_patch(self.point)

class Points:
    """
    Cette classe réprésente l'ensemble des points tracées de la figure.
    """
    def __init__(self):
        """
        Constructeur de la classe Points.
        """
        self.points = []

    def add(self, point: Point):
        """
        Cette méthode permet l'ajout d'un point dans la liste des points

        Args:
            - point: instance de la classe Point
        """
        self.points.append(point)

    def clear(self, point: Point):
        """
        Cette méthode permet de supprimer un point dans la liste des points.

        Args:
            - point: instance de la classe Point
        """
        if(point in self.points):   
            self.points.remove(point)
            point.point.remove()

    def clear_all(self):
        """
        Cette méthode permet de supprimer l'ensemble des points dans la liste
        """
        for point in self.points:
            point.point.remove()
        self.points.clear()

class Rectangle:
    """
    Cette classe permet de tracer des rectangles.
    """
    def __init__(self, label: str, x1: float, y1: float, x2: float, y2: float):
        """
        Constructeur de la classe rectangle.
        
        Args:
            - label: classe du point
            - x1: coordonnée minimale abscisse 
            - y1: coordonnée minimale ordonnée
            - x2: coordonnée maximale abscisse
            - y2: coordonnée maximale ordonnée
        """
        self.label = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.create_rectangle()
    
    def create_rectangle(self):
        """
        Cette méthode crée un rectangle.
        """
        if(self.label == ""):
            self.rectangle = plt.Rectangle((self.x1, self.y1), self.x2, self.y2, edgecolor="black", fill=False)
        else:
            if(self.label in color):
                self.rectangle = plt.Rectangle((self.x1, self.y1), self.x2, self.y2, edgecolor=color[self.label], fill = False)

    def update_rectangle(self, x2: float, y2: float):
        """
        Cette méthode met à jour les valeurs du rectangle.
        """
        self.x2 = x2
        self.y2 = y2

        x_min = min(self.x1, self.x2)
        y_min = min(self.y1, self.y2)
        width = abs(self.x2 - self.x1)
        height = abs(self.y2 - self.y1)

        """
        self.rectangle.set_width(width)
        self.rectangle.set_height(height)
        self.rectangle.set_xy((x_min, y_min))
        """
        if(self.label == ""):
            self.rectangle = plt.Rectangle((x_min, y_min), width, height, facecolor = color[self.label], edgecolor = color[self.label],  fill=True, alpha = 0.3)
        else:
            if(self.label in color):
                self.rectangle = plt.Rectangle((x_min, y_min), width, height, facecolor = color[self.label], edgecolor = color[self.label], fill=True, alpha = 0.3)

    def get_ord_data(self):
        """
        Cette méthode permet de mettre à jour les maximums et minimums des abscisses et des ordonnées.
        """
        if(self.x1 > self.x2):
            x1 = self.x2
            x2 = self.x1
        else:
            x1 = self.x1
            x2 = self.x2
        if(self.y1 > self.y2):
            y1 = self.y2
            y2 = self.y1
        else:
            y1 = self.y1
            y2 = self.y2
        return x1, y1, x2, y2

    def temporary_plot(self, axes):
        """
        Cette méthode affiche temporairement le rectangle.

        Args:
            - axes: Axes de la figure
        """
        axes.draw_artist(self.rectangle)

    def plot(self, axes):
        """
        Cette méthode affiche le rectangle.

        Args:
            - axes: Axes de la figure
        """
        axes.add_patch(self.rectangle)

    def clear(self):
        """
        Cette méthode affiche temporairement le rectangle.

        """
        self.rectangle.remove()

class Rectangles:
    def __init__(self):
        self.rectangles = []

    def add(self, rectangle: Rectangle):
        self.rectangles.append(rectangle)

    def clear(self,rectangle: Rectangle):
        if(rectangle in self.rectangles):   
            rectangle.rectangle.remove()
            self.rectangles.remove(rectangle)

    def clear_all(self):
        for rectangle in self.rectangles:
            rectangle.rectangle.remove()
        self.rectangles.clear()

class Pointer:
    def __init__(self, x: None | float, y: None | float, parent):
        self.x = x
        self.y = y
        self.parent = parent

        self.vline = None
        self.hline = None

    def set(self, x: float, y: float):
        self.x = x
        self.y = y

    def instant_pointer_data(self):
        xindex = self.parent.Xunit.index(self.parent.abs_unit.currentText())
        yindex = self.parent.Yunit.index(self.parent.ord_unit.currentText())
        self.parent.xpointer_instant_label.setText("{:.2f} {}".format(self.x, self.parent.xLabel[xindex]))
        self.parent.ypointer_instant_label.setText("{:.2f} {}".format(self.y, self.parent.yLabel[yindex]))


    def plot(self, axes):
        xindex = self.parent.Xunit.index(self.parent.abs_unit.currentText())
        yindex = self.parent.Yunit.index(self.parent.ord_unit.currentText())
        self.parent.xpointer_label.setText("Abscisse: {:.2f} {}".format(self.x, self.parent.xLabel[xindex]))
        self.parent.ypointer_label.setText("Ordonnée: {:.2f} {}".format(self.y, self.parent.yLabel[yindex]))

        xmin, xmax = self.parent.axes.get_xlim()
        ymax, ymin =self.parent.axes.get_ylim()
        if(self.vline != None and self.hline != None):
            axes.lines.pop()
            axes.lines.pop()

        xline = [self.x - xmax*0.01, self.x + xmax*0.01]
        yline = [self.y - ymax*0.01, self.y + ymax*0.01]

        if(yline[0] < ymin):
            yline[0] = self.y
        if(yline[1] > ymax):
            yline[1] = self.y
        self.vline = axes.plot([self.x, self.x], yline, color='red', linewidth=1)

        if(xline[0] < xmin):
            xline[0] = self.x
        if(xline[1] > xmax):
            xline[1] = self.x
        self.hline = axes.plot( xline, [self.y, self.y], color='red', linewidth=1)

    def clear(self, axes):
        if(self != None):
            if(self.vline != None and self.hline != None):
                my_os = platform.system()
                if(my_os == "Linux" or my_os== "Darwin"):
                    axes.lines.pop()
                    axes.lines.pop()
                else:
                    if(my_os == "Windows"):
                        for line in axes.lines:
                            line.remove()
                self.vline = None
                self.hline = None
            self.parent.xpointer_label.setText("")
            self.parent.ypointer_label.setText("")