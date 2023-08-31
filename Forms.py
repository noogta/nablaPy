import matplotlib.pyplot as plt
color = {
    "": "black",
    "Acier": "brown", 
    "Anomalie franche": "red",
    "Anomalie hétérogène": "green",
    "Réseaux": "blue", 
    "Autres": "purple"
}

class Point:
    def __init__(self, label: str, x: float, y: float, rel: float):
        self.label = label
        self.x = x
        self.y = y
        self.create_point(relation=rel)
    
    def create_point(self, relation: float):
        if(self.label == ""):
            print(relation)
            self.point = plt.Circle((self.x, self.y), radius=relation, color='black', alpha = 1)
        else:
            if(self.label in color):
                self.point = plt.Circle((self.x, self.y), radius=relation, color=color[self.label], alpha = 1)

    def update_point(self, x: float, y: float):
        # Mise à jour des coordonnées
        self.x = x
        self.y = y
        self.point.center = (self.x, self.y)

    def plot(self, axes):
        axes.add_patch(self.point)

class Points:
    def __init__(self):
        self.points = []

    def add(self, point: Point):
        self.points.append(point)

    def clear(self, point: Point):
        if(point in self.points):   
            self.points.remove(point)
            point.point.remove()

    def clear_all(self):
        for point in self.points:
            point.point.remove()
        self.points.clear()

class Rectangle:
    def __init__(self, label: str, x1: float, y1: float, x2: float, y2: float):
        self.label = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.create_rectangle()
    
    def create_rectangle(self):
        if(self.label == ""):
            self.rectangle = plt.Rectangle((self.x1, self.y1), self.x2, self.y2, edgecolor="black", fill=False)
        else:
            if(self.label in color):
                self.rectangle = plt.Rectangle((self.x1, self.y1), self.x2, self.y2, edgecolor=color[self.label], fill=False)

    def update_rectangle(self, x2: float, y2: float):
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
            self.rectangle = plt.Rectangle((x_min, y_min), width, height, edgecolor="black", fill=False)
        else:
            if(self.label in color):
                self.rectangle = plt.Rectangle((x_min, y_min), width, height, edgecolor=color[self.label], fill=False)

    def get_ord_data(self):
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
        axes.draw_artist(self.rectangle)

    def plot(self, axes):
        axes.add_patch(self.rectangle)

    def clear(self):
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
                axes.lines.pop()
                axes.lines.pop()
                self.vline = None
                self.hline = None
            self.parent.xpointer_label.setText("")
            self.parent.ypointer_label.setText("")