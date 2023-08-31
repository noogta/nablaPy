from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import sqrt
from RadarData import cste_global
from Forms import Point, Points, Rectangle, Rectangles, Pointer
from Export import ExJsonRectangle, ExJsonPoint, ExJsonNone
import os
CURSOR_DEFAULT = Qt.CursorShape.ArrowCursor
CURSOR_POINT = Qt.CursorShape.PointingHandCursor
CURSOR_DRAW = Qt.CursorShape.CrossCursor
CURSOR_MOVE = Qt.CursorShape.ClosedHandCursor
CURSOR_GRAB = Qt.CursorShape.OpenHandCursor
CURSOR_BUSY = Qt.CursorShape.BusyCursor
CURSOR_WAIT = Qt.CursorShape.WaitCursor
CURSOR_MODIFIED_POINT = Qt.CursorShape.SizeAllCursor
CURSOR_MODIFIED_POINT_RECTANGLE = Qt.CursorShape.OpenHandCursor

class Canvas:
    def __init__(self, figure: Figure, axes, mainwindow):
        self.canvas = FigureCanvas(figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.axes = axes
        self.mainwindow = mainwindow
        
        self.Pointer = Pointer(None, None, self.mainwindow)
        self.Point = None
        self.Rectangle = None

        self.Points = Points()
        self.Rectangles = Rectangles()
        self.shapes = []

        self.mode = "Pointer"
        self._prec = None

        self.canvas.mpl_connect('button_press_event', self.MousePressEvent)
        self.canvas.mpl_connect('motion_notify_event', self.MouseMoveEvent)
        self.canvas.mpl_connect('button_release_event', self.MouseReleaseEvent)
        self.canvas.mpl_connect('pick_event', self.on_rect_pick)


    def set_mode(self, mode: str, button):
        """
        Méthode qui permet de définir le mode de la classe.
        """
        if(self._prec == button):
            button.setStyleSheet("")
            self.mode = "Pointer"
            self._prec = None
        else:
            if(self._prec != None):
                self._prec.setStyleSheet("")
            button.setStyleSheet("""     
            QPushButton:active {
                background-color: #45a049;}""")
            self.mode = mode
            self._prec = button
        self.update_cursor()
    
    def update_cursor(self):
        if(self.mode == "Point"):
            self.canvas.setCursor(CURSOR_POINT)
        else:
            if(self.mode == "Rectangle"):
                self.canvas.setCursor(CURSOR_DRAW)
            else:
                self.canvas.setCursor(CURSOR_DEFAULT)

    def MousePressEvent(self, event):
        if event.button == 1:
            x = event.xdata
            y = event.ydata
            # Vérifier si les coordonnées sont valides
            if x is not None and y is not None:
                if(self.mode == "Pointer"):
                    self.Pointer.set(x, y)
                    self.Pointer.plot(self.axes)

                    self.canvas.draw()
                else:
                    if(self.mode == "Rectangle"):
                        # Sauvegarder le fond de la toile pour utiliser blit
                        #self.background = self.canvas.copy_from_bbox(self.axes.bbox)
                        # Dessiner le Rectangle temporaire
                        self.Rectangle = Rectangle(self.mainwindow.class_choice.currentText(), x, y, 0., 0.)
                        self.Rectangle.plot(self.axes)
        else:
            if(event.button == 3):
                print("test")

    def MouseMoveEvent(self, event):
        # Récupérer les coordonnées de la souris pendant le glissement
        x2 = event.xdata
        y2 = event.ydata

        # Vérifier si les coordonnées sont valides
        if x2 is not None and y2 is not None:

            # Mise à jour Pointeur instantanné
            #self.Pointer.set(x2, y2)
            #self.Pointer.instant_pointer_data()

            # Mode rectangle
            if(self.mode == "Rectangle"):
                if(event.button == 1):
                    # Mettre à jour les propriétés du Rectangle temporaire
                    self.Rectangle.update_rectangle(x2, y2)

                    # Utiliser blit pour mettre à jour seulement le Rectangle
                    #self.canvas.restore_region(self.background)
                    self.Rectangle.temporary_plot(self.axes)
                    #self.canvas.blit(self.axes.bbox)
    
    def MouseReleaseEvent(self, event):
        if(self.mode == "Point"):
            if(event.button == 1):
                # Récupérer les coordonnées du relâchement de la souris
                x = event.xdata
                y = event.ydata
                # Vérifier si les coordonnées sont valides
                if(x is not None and y is not None):
                    xmax = self.mainwindow.axes.get_xlim()[1]
                    ymax = self.mainwindow.axes.get_ylim()[0]
                    minimum = min(xmax, ymax)
                    maximum = max(xmax, ymax)
                    self.Point = Point(self.mainwindow.class_choice.currentText(), x, y, minimum / maximum)
                    self.Points.add(self.Point)
                    self.shapes.append(self.Point)
                    self.mainwindow.shape_list.addItem(str(self.Point.label)+"(Point,"+str(round(x,2))+","+str(round(y,2))+")")

                    self.Point.plot(self.axes)

                    self.canvas.draw()
        else:
            if(self.mode == "Rectangle"):
                if(event.button == 1):
                    # Récupérer les coordonnées du relâchement de la souris
                    x = event.xdata
                    y = event.ydata

                    # Vérifier si les coordonnées sont valides
                    if(x is not None and y is not None):
                        # Dessiner le Rectangle final
                        self.Rectangle.update_rectangle(x, y)
                        if(self.Rectangle.x1 != self.Rectangle.x2 and self.Rectangle.y1 != self.Rectangle.y2):
                            self.Rectangle.plot(self.axes)
                            self.Rectangles.add(self.Rectangle)
                            self.shapes.append(self.Rectangle)

                            x1, y1, x2, y2 = self.Rectangle.get_ord_data()
                            self.mainwindow.shape_list.addItem(str(self.Rectangle.label)+"(Rectangle,"+str(round(x1,2))+","+str(round(y1,2))+","+str(round(x2,2))+","+str(round(y2,2))+")")

                        self.canvas.draw()

    def on_rect_pick(self, event):
        print(event.artist)

    def reset_axes(self, axes, mainwindow):
        # Réinitialisation de l'axe
        self.axes = axes
        
        self.Pointer = Pointer(None, None, mainwindow)
        self.Point = None
        self.Rectangle = None

        self.Points = Points()
        self.Rectangles = Rectangles()
        self.shapes.clear()

    def clear_pointer(self):
        self.Pointer.clear(self.axes)
        self.canvas.draw()

    def clear_point(self, index):
        point = self.shapes[index]
        if point in self.Points.points:
            self.mainwindow.shape_list.takeItem(index)
            self.shapes.remove(point)
            self.Points.clear(point)
            self.canvas.draw()

    def clear_points(self):
        for point in self.Points.points:
            index = self.shapes.index(point)
            self.mainwindow.shape_list.takeItem(index)
            self.shapes.remove(point)
        self.Points.clear_all()

        self.canvas.draw()

    def clear_rectangle(self, index):
        rectangle = self.shapes[index]
        if rectangle in self.Rectangles.rectangles:
            self.mainwindow.shape_list.takeItem(index)
            self.shapes.remove(rectangle)
            self.Rectangles.clear(rectangle)
            self.canvas.draw()

    def clear_rectangles(self):
        for rectangle in self.Rectangles.rectangles:
            index = self.shapes.index(rectangle)
            self.mainwindow.shape_list.takeItem(index)
            self.shapes.remove(rectangle)
        self.Rectangles.clear_all()

        self.canvas.draw()

    def clear_list(self):
        self.mainwindow.shape_list.clear()


    def clear_canvas(self):
        self.clear_pointer()
        self.clear_points()
        self.clear_rectangles()
        
        self.canvas.draw()

    def del_element(self):
        selected_item = self.mainwindow.shape_list.currentItem()  # Récupère l'élément sélectionné
        if selected_item:
            text = selected_item.text()  # Récupère le texte de l'élément
            index = self.mainwindow.shape_list.row(selected_item)  # Récupère l'index de l'élément

            if "Point" in text:
                self.clear_point(index)
            elif "Rectangle" in text:
                self.clear_rectangle(index)

    def export_json(self):
        n_tr = self.mainwindow.feature[0]
        n_samp = self.mainwindow.feature[1]
        if(self.mainwindow.def_value != None):
            d_max = self.mainwindow.def_value
        else:
            d_max = self.mainwindow.feature[2]
        t_max = self.mainwindow.feature[3]
        p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.mainwindow.epsilon_value)) / 2
        step_time = self.mainwindow.feature[5]

        L_xmax = [d_max, step_time*n_tr, n_tr]
        L_ymax = [p_max, t_max, n_samp]

        xindex = self.mainwindow.Xunit.index(self.mainwindow.abs_unit.currentText())
        yindex = self.mainwindow.Yunit.index(self.mainwindow.ord_unit.currentText())

        if(self.mainwindow.cb_value != 0 and self.mainwindow.ce_value == None):
            #print(f"Avant:{L_ymax[yindex]}")
            L_ymax[yindex] = L_ymax[yindex] - (self.mainwindow.cb_value / n_samp) * L_ymax[yindex]
            #print(f"Après:{L_ymax[yindex]}")

        else:
            if(self.mainwindow.cb_value != 0 and self.mainwindow.ce_value != None):
                #print(f"Avant:{L_ymax[yindex]}")
                L_ymax[yindex] = L_ymax[yindex] * (self.mainwindow.ce_value - self.mainwindow.cb_value) / n_samp
                #print(f"Après:{L_ymax[yindex]}")
            else:
                if(self.mainwindow.cb_value == 0 and self.mainwindow.ce_value != None):
                    #print(f"Avant:{L_ymax[yindex]}")
                    L_ymax[yindex] = (self.mainwindow.ce_value / n_samp) * L_ymax[yindex]
                    #print(f"Après:{L_ymax[yindex]}")
        if(len(self.shapes) != 0):
            for shape in self.shapes:
                if isinstance(shape,Rectangle):
                    x1, y1, x2, y2 = shape.get_ord_data()
                    x1, x2 = x1 / L_xmax[xindex], x2 / L_xmax[xindex]
                    y1, y2 = y1 / L_ymax[yindex], y2 / L_ymax[yindex]
                    ExJsonRectangle(self.mainwindow.img_modified, self.mainwindow.selected_file[:-4], shape.label, x1, y1, x2, y2)
                else:
                    if(isinstance(shape, Point)):
                        x, y = shape.x,shape.y
                        x = x / L_xmax[xindex]
                        y = y / L_ymax[yindex]
                        ExJsonPoint(self.mainwindow.img_modified, self.mainwindow.selected_file[:-4], shape.label, shape.x, shape.y)
            self.clear_canvas()
        else:
            ExJsonNone(self.mainwindow.img_modified, self.mainwindow.selected_file[:-4])

    def test_list(self):
        print(f"Taille de la liste QListWidget: {self.mainwindow.shape_list.count()}")
        print(f"Taille de shapes: {len(self.shapes)}")
        print(f"Taille des Points: {len(self.Points.points)}")
        print(f"Taille de Rectangles: {len(self.Rectangles.rectangles)}")
    