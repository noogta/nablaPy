import matplotlib.pyplot as plt
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Canvas(FigureCanvas):
    def __init__(self, figure, axes, parent):
        self.canvas = FigureCanvas(figure)
        self.axes = axes
        self.parent = parent

        self.points = []
        self.squares = []

        self.drawing_rectangle = None
        self.start_point = None

        self.vline = None
        self.hline = None

        self.canvas.mpl_connect('button_press_event', self.pointer)

    def pointer(self, event):
        x = event.xdata
        y = event.ydata

        xindex = self.parent.Xunit.index(self.parent.abs_unit.currentText())
        yindex = self.parent.Yunit.index(self.parent.ord_unit.currentText())
        
        if x is not None and y is not None:
            self.parent.xpointer_label.setText("{:.2f} {}".format(x, self.parent.xLabel[xindex]))
            self.parent.ypointer_label.setText("{:.2f} {}".format(y, self.parent.yLabel[yindex]))
            """

            # Supprimer les anciennes lignes du viseur s'il y en a
            if self.vline is not None and self.hline is not None:
                self.vline.remove()
                self.hline.remove()
            # Dessiner le pointeur sur le canvas
            self.vline = self.axes.plot([x, x], [y - 0.20, y + 0.20], color='red', linewidth=1)
            self.hline = self.axes.plot([x - 0.20, x + 0.20], [y, y], color='red', linewidth=1)

            self.canvas.draw()
            """
    def clear_canvas(self):
        for point in self.points:
            self.axes.plot(point[0], point[1], 'ro')
        self.points = []

        for square in self.squares:
            square.remove()
        self.squares = []

        for line in self.viseur_lines:
            print(line)
        self.viseur_lines = None

        # Mettre à jour le canvas
        self.canvas.draw()

