import sys
import traceback
import os
import numpy as np
import platform
from RadarController import RadarController
from RadarData import RadarData, cste_global
from QCanvas import Canvas
from math import sqrt, floor, ceil
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QListWidget, QPushButton, QComboBox, QLineEdit, QTabWidget, QCheckBox
from PyQt6.QtGui import QAction, QFont
from matplotlib.figure import Figure

my_os = platform.system()
if(my_os == "Linux" or my_os== "Darwin"):
    xSIZE, ySIZE = (1720,900)
else:
    if(my_os == "Windows"):
        xSIZE, ySIZE= (1080,800)

class MainWindow():
    """Cette classe représente la fenêtre principale."""
    def __init__(self, softwarename: str):
        """
        Construteur de la classe MainWindow.

        Args:
            softwarename (str): Nom de l'application
        """
        # Création de notre fenêtre principale
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(softwarename)
        

        # Définition de la taille de la fenêtre
        self.window.setGeometry(0, 0, xSIZE, ySIZE)

        # À définir à la fin
        #self.window.setMaximumWidth(QScreen().availableGeometry().width())
        #self.window.setMaximumHeight(QScreen().availableGeometry().height())

        # Placement de la fenêtre au milieu de l'écran
        #self.center_window()

        # Variables états
        self.ext_list = [".rd7", ".rd3", ".DZT"]
        self.freq_state = ["Filtrage désactivé", "Haute Fréquence", "Basse Fréquence"]
        self.inv_list_state = "off"
        self.dewow_state = "off"
        self.inv_state = "off"
        self.equal_state = "off"

        # Initialisation figure, axes, canvas
        self.figure = Figure(figsize=(12, 8), facecolor='none')
        self.axes = self.figure.add_subplot(1,1,1)
        self.QCanvas = Canvas(self.figure, self.axes, self)

        # Affichage des différents blocs
        self.menu()
        self.main_block()
        
        # Valeurs
        self.gain_const_value = 1.
        self.gain_lin_value = 0.
        self.t0_lin_value = 0
        self.gain_exp_value = 0.
        self.t0_exp_value = 0
        self.epsilon_value = 6.
        self.sub_mean_value = None
        self.cutoff_value = None
        self.sampling_value = None
        self.cb_value = 0
        self.ce_value = None
        self.feature = None
        self.def_value = None

        # Variables
        self.prec_abs = None
        self.prec_ord = None
        self.selected_file = None

        
        # Unités et labels
        self.Xunit = ["Distance", "Temps d'acquésition", "Traces"]
        self.Yunit = ["Profondeur", "Temps", "Samples"]
        self.Xlabel = ["Distance en m", "Temps en s", "Traces"]
        self.Ylabel = ["Profondeur en m", "Temps en ns", "Samples"]
        self.xLabel = ["m", "s", "mesures"]
        self.yLabel = ["m", "ns", "samples"]

        # 
        self.radargram()
        self.sidebar()
    
    def show(self):
        """
        Affiche la fenêtre du logiciel.
        """
        # Affichage de la fenêtre
        self.window.show()
        sys.exit(self.app.exec())

    def menu(self):
        """
        Affiche le menu et créer les actions du logiciel
        """
        # Création de la barre de menu
        menu_bar = self.window.menuBar()
        
        # Création des différents Menus
        file_menu = menu_bar.addMenu("Fichier")
        modified_menu = menu_bar.addMenu("Modifier")
        Window_menu = menu_bar.addMenu("Fenêtre")
        help_menu = menu_bar.addMenu("Aide")

        # Création des actions pour le menu "Fichier"
        open_folder_action = QAction("Ouvrir un dossier", self.window)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        save_img_action = QAction("Sauvegarder l'image", self.window)
        save_img_action.triggered.connect(self.save)
        file_menu.addAction(save_img_action)

        save_imgs_action = QAction("Sauvegarder les images", self.window)
        save_imgs_action.triggered.connect(self.save_all)
        file_menu.addAction(save_imgs_action)

        file_menu.addSeparator()

        export_action = QAction("Exporter les bbox", self.window)
        export_action.triggered.connect(self.QCanvas.export_json)
        file_menu.addAction(export_action)

        export_none_action = QAction("Exporter None", self.window)
        export_none_action.triggered.connect(self.export_none)
        file_menu.addAction(export_none_action)

        export_nones_action = QAction("Exporter les Nones", self.window)
        export_nones_action.triggered.connect(self.export_nones)
        file_menu.addAction(export_nones_action)

        file_menu.addSeparator()

        quit_action = QAction("Quitter", self.window)
        quit_action.triggered.connect(self.window.close)
        file_menu.addAction(quit_action)

        # Création des actions pour le menu "Modifier"
        del_pointer = QAction("Supprimer le pointeur", self.window)
        del_pointer.triggered.connect(self.QCanvas.clear_pointer)
        modified_menu.addAction(del_pointer)

        del_points = QAction("Supprimer les points", self.window)
        del_points.triggered.connect(self.QCanvas.clear_points)
        modified_menu.addAction(del_points)

        del_rectangles = QAction("Supprimer les rectangles", self.window)
        del_rectangles.triggered.connect(self.QCanvas.clear_rectangles)
        modified_menu.addAction(del_rectangles)

        del_canvas = QAction("Supprimer les éléments du canvas", self.window)
        del_canvas.triggered.connect(self.QCanvas.clear_canvas)
        modified_menu.addAction(del_canvas)


    def main_block(self):
        """
        Affiche et paramètre les différents blocs du logiciel.
        """
        # Limites des  dimensions
        min_height = 650
        min_width_sidebar = 330
        min_width_radargram = 600

        # Widget central pour contenir le layout principal
        main_widget = QWidget()
        self.window.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Ajout du Menu
        main_layout.setMenuBar(self.window.menuBar())

        # Sidebar
        self.sidebar_widget = QWidget()

        # Définir la taille limite du sidebar
        self.sidebar_widget.setMinimumHeight(min_height)
        self.sidebar_widget.setFixedWidth(min_width_sidebar)

        # Radargram
        self.radargram_widget = QWidget()

        # Définir la taille limite du radargramme
        self.radargram_widget.setMinimumWidth(min_width_radargram)
        self.radargram_widget.setMinimumHeight(min_height)

        # Layout horizontal pour placer le sidebar et le radargramm côte à côte
        contents_layout = QHBoxLayout()
        contents_layout.addWidget(self.sidebar_widget)
        contents_layout.addWidget(self.radargram_widget)
        main_layout.addLayout(contents_layout)

    def open_folder(self):
        """
        Méthode permettant d'ouvrir une fenêtre afin de choisir un dossier
        """
        try:
            # Dossier sélectionné et mise à jour de la liste des fichiers
            self.selected_folder = QFileDialog.getExistingDirectory(self.window, "Ouvrir un dossier", directory="/data/Documents/GM/Ing2-GMI/Stage/Mesure")
            self.update_files_list()

            # Supprimer le contenu des entrées de découpage
            self.cb_entry.clear()
            self.ce_entry.clear()

        except:
            print(f"Erreur lors de la sélection du dossier:")
            traceback.print_exc()

    def update_files_list(self):
        """
        Méthode qui met à jour la liste des fichiers du logiciel.
        """
        # Création de la variable de type list str, self.file_list
        try:
            if(self.selected_folder != ""):
                # Récupération de la liste des fichiers du dossier
                self.files_list = os.listdir(self.selected_folder)

                # Trie de la liste
                self.files_list.sort()

                # Suppresion --> Actualisation de la listbox
                self.listbox_files.clear()

                # États/Formats pour le filtrage par fréquence
                format_freq_list = ["", "_1", "_2"]
                index_freq = self.freq_state.index(self.filter_button.text())

                # États pour le filtrage par format
                index_format = self.ext_list.index(self.mult_button.text())

                # Filtrage selon les différents critères
                for file in self.files_list:
                    if (file.endswith(self.ext_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or self.freq_state[index_freq] == "Filtrage désactivé"):
                        self.listbox_files.addItem(file)
                    else:
                        if (file.endswith(self.ext_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or self.freq_state[index_freq] == "Filtrage désactivé"):
                            self.listbox_files.addItem(file)
            else:
                print("Aucun dossier n'a été sélectionné.")
        except:
            print("Erreur lors de la mise à jour de la liste des fichiers:")
            traceback.print_exc()

    def save(self):
        """
        Méthode qui sauvegarde l'image sous le format souhaité (.jpeg ou .png).
        """
        try:
            if self.file_path == "":
                print("Aucune image n'a encore été définie")
            else:
                file_save_path, _ = QFileDialog.getSaveFileName(self.window, "Sauvegarder l'image", "", "PNG files (*.png);;JPEG files (*.jpeg)")
                if file_save_path:
                    self.figure.savefig(file_save_path)
                    print("L'image a été sauvegardée avec succès !")
        except:
            print("Erreur lors de la sauvegarde de l'image.")
            traceback.print_exc()
    
    def save_all(self):
        """
        Méthode qui sauvegarde l'ensemble des images issus du dossier sous le format souhaité .png.
        """
        try:
            folder_path = QFileDialog.getExistingDirectory(self.window, "Sauvegarde des images")
            files = [self.listbox_files.item(row).text() for row in range(self.listbox_files.count())]
            prec_selected_file = self.selected_file
            for file in files:
                self.selected_file = file
                self.Rdata = RadarData(self.selected_folder + "/"+ file)
                self.feature = self.Rdata.get_feature()

                self.update_canvas_image()

                self.img = self.Rdata.rd_img()
                self.img_modified = self.img[int(self.cb_value):int(self.ce_value), :]

                if(self.dewow_state == "on"):
                    self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

                if(self.cutoff_entry.text() != '' and self.sampling_entry.text() != ''):
                    self.img_modified = self.Rcontroller.low_pass(self.img_modified, self.cutoff_value, self.sampling_value)

                if(self.sub_mean_value != None):
                    self.img_modified = self.Rcontroller.sub_mean(self.img_modified, self.sub_mean_value)

                if(self.inv_list_state == "on"):
                    if(files.index(file) % 2 != 0):
                        self.img_modified = np.fliplr(self.img_modified)

                if(self.inv_state == "on"):
                    self.img_modified = np.fliplr(self.img_modified)

                self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)

                if(self.equal_state == "on"):
                    if self.img_modified.shape[1] < self.max_tr:
                        # Ajout des colonnes supplémentaires
                        additional_cols = self.max_tr - self.img_modified.shape[1]
                        self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')            

                self.update_axes(self.def_value, self.epsilon_value)

                # Sauvegarder l'image en format PNG
                file_save_path = folder_path + "/" + file[:-4] + ".png"
                self.figure.savefig(file_save_path)

            # 
            self.selected_file = prec_selected_file
            self.Rdata = RadarData(self.file_path)
            self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Erreur lors de la sauvegarde des images.")
            traceback.print_exc()

    def export_none(self):
        """
        Méthode qui appelle la méthode export_json pour l'image sélectionnée.
        """
        try:
            self.QCanvas.export_json()
        except:
            print("Erreur lors de l'exportation de l'image/bbox.")
            traceback.print_exc()           

    def export_nones(self):
        """
        Méthode qui appelle la méthode export_json pour l'ensemble des images sur dossier sélectionné.
        """
        try:
            files = [self.listbox_files.item(row).text() for row in range(self.listbox_files.count())]
            prec_selected_file = self.selected_file
            for file in files:
                self.selected_file = file
                self.Rdata = RadarData(self.selected_folder + "/" + file)
                self.feature = self.Rdata.get_feature()

                self.update_canvas_image()

                self.img = self.Rdata.rd_img()
                self.img_modified = self.img[int(self.cb_value):int(self.ce_value), :]

                if(self.dewow_state == "on"):
                    self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

                if(self.cutoff_entry.text() != '' and self.sampling_entry.text() != ''):
                    self.img_modified = self.Rcontroller.low_pass(self.img_modified, self.cutoff_value, self.sampling_value)

                if(self.sub_mean_value != None):
                    self.img_modified = self.Rcontroller.sub_mean(self.img_modified, self.sub_mean_value)

                if(self.inv_list_state == "on"):
                    if(files.index(file) % 2 != 0):
                        self.img_modified = np.fliplr(self.img_modified)

                if(self.inv_state == "on"):
                    self.img_modified = np.fliplr(self.img_modified)

                self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)

                if(self.equal_state == "on"):
                    if self.img_modified.shape[1] < self.max_tr:
                        # Ajout des colonnes supplémentaires
                        additional_cols = self.max_tr - self.img_modified.shape[1]
                        self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')            

                self.QCanvas.export_json()
                # Sauvegarder l'image en format PNG
            # 
            self.selected_file = prec_selected_file
            self.Rdata = RadarData(self.file_path)
            self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Erreur lors de l'exportation des images/bbox.")
            traceback.print_exc()

    def sidebar(self):
        """
        Méthode qui crée les différentes blocs de sidebar.
        """
        # Couche principale (sidebar_layout)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Premier bloc: Liste des fichiers
        file_frame = QFrame()
        sidebar_layout.addWidget(file_frame)
        
        list_layout = QVBoxLayout(file_frame)
        title_file_layout = QVBoxLayout()
        list_layout.addLayout(title_file_layout)
        title_file_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        file_label = QLabel("Fichiers")
        file_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_file_layout.addWidget(file_label)

        self.listbox_files = QListWidget()
        self.listbox_files.clicked.connect(self.select_file)
        list_layout.addWidget(self.listbox_files)

        button_layout = QHBoxLayout()
        list_layout.addLayout(button_layout)

        self.filter_button = QPushButton("Filtrage désactivé")
        self.filter_button.clicked.connect(self.filter_list_file)
        button_layout.addWidget(self.filter_button)

        self.mult_button = QPushButton(".rd7")
        self.mult_button.clicked.connect(self.filter_mult)
        button_layout.addWidget(self.mult_button)

        self.inv_list_button = QPushButton("Inversement pairs")
        self.inv_list_button.clicked.connect(self.inv_file_list)
        list_layout.addWidget(self.inv_list_button)

        # Deuxième bloc: Affichage
        display_frame = QFrame()
        sidebar_layout.addWidget(display_frame)

        display_layout = QVBoxLayout(display_frame)
        title_display_layout = QVBoxLayout()
        display_layout.addLayout(title_display_layout)
        title_display_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        display_label = QLabel("Affichage")
        display_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_display_layout.addWidget(display_label)

        display_notebook = QTabWidget()
        display_layout.addWidget(display_notebook)

        # Premier onglet: Axes
        axes_wid_ntb = QWidget()
        display_notebook.addTab(axes_wid_ntb, "Axes")

        axes_layout = QVBoxLayout(axes_wid_ntb)

        abs_label_layout = QHBoxLayout()
        abs_label_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        axes_layout.addLayout(abs_label_layout)

        abs_label = QLabel("Unité en abscisse:")
        abs_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        abs_label_layout.addWidget(abs_label)

        self.abs_unit = QComboBox()
        self.abs_unit.addItems(["Distance", "Temps d'acquésition", "Traces"])
        self.abs_unit.setCurrentText("Distance")
        self.abs_unit.currentTextChanged.connect(lambda: self.update_axes(self.def_value, self.epsilon_value))
        axes_layout.addWidget(self.abs_unit)

        def_layout = QHBoxLayout()
        axes_layout.addLayout(def_layout)

        self.def_label = QLabel("Définir la Distance")
        def_layout.addWidget(self.def_label)

        self.def_entry = QLineEdit()
        self.def_entry.setPlaceholderText("en m")
        def_layout.addWidget(self.def_entry)

        def update_def_value():
            """
            Méhode qui met à jour self.def_value.

            Returns:
                self.def_value: défini de la distance.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.def_entry)

                # Récupération de la valeur def
                self.def_value = float(self.def_entry.text())

                # Vérification
                if(self.def_value < 0.):
                    self.QLineError(self.def_entry,"Erreur: d > 0")
                    self.def_value = None # Valeur par défaut en cas d'erreur

                else:
                    self.def_entry.setPlaceholderText(str(self.def_value))

            except:
                # Réinitialisation de l'entrée
                self.def_value = None  # Valeur par défaut en cas d'erreur de conversion
                self.def_entry.clear()
                self.def_entry.setPlaceholderText("")
            return self.def_value
            
        self.def_entry.editingFinished.connect(lambda: self.update_axes(update_def_value(), self.epsilon_value))

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)  # Utilisation de Shape.HLine
        axes_layout.addWidget(separator)

        ord_label_layout = QHBoxLayout()
        ord_label_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        axes_layout.addLayout(ord_label_layout)

        ord_label = QLabel("Unité en ordonnée:")
        ord_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        ord_label_layout.addWidget(ord_label)

        self.ord_unit = QComboBox()
        self.ord_unit.addItems(["Profondeur", "Temps", "Samples"])
        self.ord_unit.setCurrentText("Profondeur")
        self.ord_unit.currentTextChanged.connect(lambda: self.update_axes(self.def_value, self.epsilon_value))
        axes_layout.addWidget(self.ord_unit)

        epsilon_layout = QHBoxLayout()
        axes_layout.addLayout(epsilon_layout)

        self.epsilon_label = QLabel("\u03B5 (permitivité)")
        self.epsilon_label.setFont(QFont("Arial", 12))
        epsilon_layout.addWidget(self.epsilon_label)

        self.epsilon_entry = QLineEdit()
        self.epsilon_entry.setPlaceholderText(str(self.epsilon_value))
        epsilon_layout.addWidget(self.epsilon_entry)

        def update_epsilon_value():
            """
            Méhode qui met à jour self.epsilon_value.

            Returns:
                self.epsilon_value: défini la permittivité.
            """
            try:
                # Réinitialisation de l'aspect d'epsilon
                self.reset_style(self.epsilon_entry)
                
                # Récupération de la valeur epsilon
                self.epsilon_value = float(self.epsilon_entry.text())

                # Vérification
                if(self.epsilon_value <= 0.):
                    self.epsilon_value = 6.
                    self.QLineError(self.epsilon_entry,"Erreur: \u03B5 > 0")
            except:
                # Gestion Erreur
                self.epsilon_value = 6.
            return self.epsilon_value
        
        self.epsilon_entry.editingFinished.connect(update_epsilon_value)
        self.epsilon_entry.editingFinished.connect(lambda: self.update_img(update_t0_lin_value(), update_t0_exp_value(), update_gain_const_value(), update_gain_lin_value(), update_gain_exp_value(), update_cb_value(), update_ce_value(), update_sub_mean(),update_cut_value()[0],update_cut_value()[1]))

        # Second onglet: Découpage
        cut_wid_ntb = QWidget()
        display_notebook.addTab(cut_wid_ntb, "Découpage")

        cut_layout = QVBoxLayout(cut_wid_ntb)
        cut_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        cut_title_fc_layout = QHBoxLayout()
        cut_title_fc_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        cut_layout.addLayout(cut_title_fc_layout)
        
        cut_underlayout = QHBoxLayout()
        cut_layout.addLayout(cut_underlayout)

        cut_label_layout = QVBoxLayout()
        cut_underlayout.addLayout(cut_label_layout)

        cut_entry_layout = QVBoxLayout()
        cut_underlayout.addLayout(cut_entry_layout)

        cut_title = QLabel("Découpage ordonée:")
        cut_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        cut_title_fc_layout.addWidget(cut_title)

        cb_label =  QLabel("Début")
        cut_label_layout.addWidget(cb_label)

        self.cb_entry = QLineEdit()
        cut_entry_layout.addWidget(self.cb_entry)

        ce_label =  QLabel("Fin")
        cut_label_layout.addWidget(ce_label)

        self.ce_entry = QLineEdit()
        cut_entry_layout.addWidget(self.ce_entry)

        def update_cb_value():
            """
            Méhode qui met à jour self.cb_value.

            Returns:
                self.cb_value: défini la découpage de début selon l'axe des ordonnées.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.cb_entry)
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon_value)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())
                L_mult = [p_max / n_samp, t_max / n_samp, 1]

                # Récupération de la valeur et gestion des erreurs
                if(self.cb_entry.text() != ''):
                    cb = float(self.cb_entry.text())
                    if(cb < 0.):
                        self.QLineError(self.cb_entry, "Erreur: y1 < 0")
                        self.cb_value = 0.
                    else:
                        if(floor(cb / L_mult[yindex]) <= self.ce_value):
                            if(self.ord_unit.currentText() == "Profondeur"):
                                self.cb_value = cb / L_mult[yindex]
                            else:
                                self.cb_value = floor(cb / L_mult[yindex])
                            self.cb_entry.setPlaceholderText(str(cb))
                        else:
                            self.cb_value = 0.
                            self.QLineError(self.cb_entry, "Erreur: y1 > y2")
                else:
                    self.cb_value = 0.
                    self.cb_entry.setPlaceholderText(str(self.cb_value))
            except:
                # Gestion erreur
                self.cb_value = 0
                self.cb_entry.setPlaceholderText(str(self.cb_value))
                self.cb_entry.clear()
            return self.cb_value

        def update_ce_value():
            """
            Méhode qui met à jour self.ce_value.

            Returns:
                self.ce_value: défini la découpage de fin selon l'axe des ordonnées.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.ce_entry)

                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon_value)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())

                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                L_ymax = [p_max, t_max, n_samp]

                # Récupération des valeurs et gestion des erreurs
                if(self.ce_entry.text() != ''):
                    ce = float(self.ce_entry.text())
                    if(ce / L_mult[yindex] < self.cb_value):
                        self.QLineError(self.ce_entry, "Erreur: y2 < y1")
                        self.ce_value = L_ymax[yindex] / L_mult[yindex]
                    else:
                        if(ce <= L_ymax[yindex]):
                            if(self.ord_unit.currentText() == "Profondeur"):
                                self.ce_value = ce / L_mult[yindex]
                            else:
                                self.ce_value = floor(ce / L_mult[yindex])
                            self.ce_entry.setPlaceholderText(str(ce))
                        else:
                            self.ce_value = L_ymax[yindex] / L_mult[yindex]
                            self.QLineError(self.ce_entry, "Erreur: y2 > max")          
                else:
                    self.ce_value = L_ymax[yindex] / L_mult[yindex]
                    self.ce_entry.setPlaceholderText(str(round(L_ymax[yindex],2)))
            except:
                # Gestion erreur
                self.ce_value = L_ymax[yindex] / L_mult[yindex]
                self.ce_entry.setPlaceholderText(str(round(L_ymax[yindex],2)))
                self.ce_entry.clear()
            return self.ce_value

        self.cb_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, update_cb_value(), self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.ce_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, update_ce_value(), self.sub_mean_value, self.cutoff_value, self.sampling_value))

        # Troisième onglet: Paramètres
        settings_wid_ntb = QWidget()
        display_notebook.addTab(settings_wid_ntb, "Paramètres")

        settings_layout = QVBoxLayout(settings_wid_ntb)
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        color_label_layout = QHBoxLayout()
        color_label_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        settings_layout.addLayout(color_label_layout)

        color_label = QLabel("Couleur:")
        color_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        color_label_layout.addWidget(color_label)

        self.color = QComboBox()
        self.color.addItems(["gray", "Greys", "viridis"])
        self.color.setCurrentText("gray")
        self.color.currentTextChanged.connect(lambda: self.update_axes(self.def_value, self.epsilon_value))
        settings_layout.addWidget(self.color)

        interpolation_label_layout = QHBoxLayout()
        interpolation_label_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        settings_layout.addLayout(interpolation_label_layout)

        interpolation_label = QLabel("Interpolation:")
        interpolation_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        interpolation_label_layout.addWidget(interpolation_label)

        self.interpolation = QComboBox()
        self.interpolation.addItems(["gaussian","nearest"])
        self.interpolation.setCurrentText("gaussian")
        self.interpolation.currentTextChanged.connect(lambda: self.update_axes(self.def_value, self.epsilon_value))
        settings_layout.addWidget(self.interpolation)

        aspect_label_layout = QHBoxLayout()
        aspect_label_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        settings_layout.addLayout(aspect_label_layout)

        aspect_label = QLabel("Aspect:")
        aspect_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        aspect_label_layout.addWidget(aspect_label)

        self.aspect = QComboBox()
        self.aspect.addItems(["auto", "equal"])
        self.aspect.setCurrentText("auto")
        self.aspect.currentTextChanged.connect(lambda: self.update_axes(self.def_value, self.epsilon_value))
        settings_layout.addWidget(self.aspect)

        # Quatrième onglet: Infos

        infos_wid_ntb = QWidget()
        display_notebook.addTab(infos_wid_ntb, "Infos")

        infos_layout = QVBoxLayout(infos_wid_ntb)
        infos_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.data_xlabel = QLabel()
        self.data_xlabel.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        infos_layout.addWidget(self.data_xlabel)

        self.data_ylabel = QLabel()
        self.data_ylabel.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        infos_layout.addWidget(self.data_ylabel)

        self.ant_radar = QLabel()
        self.ant_radar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        infos_layout.addWidget(self.ant_radar)

        # Troisième bloc: Outils
        treatment_frame = QFrame()
        treatment_frame.setMaximumHeight(330)
        sidebar_layout.addWidget(treatment_frame)

        treatment_layout = QVBoxLayout(treatment_frame)

        treatment_notebook = QTabWidget()
        treatment_layout.addWidget(treatment_notebook)

        # Premier onglet: Gains/Pointeur
        ######### Gain #########

        gain_wid_ntb = QWidget()
        treatment_notebook.addTab(gain_wid_ntb, "Gains/Pointeur")

        gain_layout = QVBoxLayout(gain_wid_ntb)
        gain_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title_gain_layout = QVBoxLayout()
        gain_layout.addLayout(title_gain_layout)
        title_gain_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        gain_label = QLabel("Gains")
        gain_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_gain_layout.addWidget(gain_label)

        under_gain_layout = QHBoxLayout()
        gain_layout.addLayout(under_gain_layout)

        label_layout = QVBoxLayout()
        under_gain_layout.addLayout(label_layout)

        entry_layout = QVBoxLayout()
        under_gain_layout.addLayout(entry_layout)

        gain_const_label = QLabel("Gain constant")
        label_layout.addWidget(gain_const_label)

        self.gain_const_entry = QLineEdit()
        self.gain_const_entry.setPlaceholderText(str(self.gain_const_value))
        entry_layout.addWidget(self.gain_const_entry)

        def update_gain_const_value():
            """
            Méhode qui met à jour self.gain_const_value.

            Returns:
                self.gain_const_value: défini le gain constant.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.gain_const_entry)

                # Récupération de la valeur
                self.gain_const_value = float(self.gain_const_entry.text())

                # Récupération des valeurs et gestion des erreurs
                if(self.gain_const_value < 1.):
                    self.QLineError(self.gain_const_entry,"Erreur: gc >= 1")
                    self.gain_const_value = 1.  # Valeur par défaut en cas d'erreur de conversion

                else:
                    self.gain_const_entry.setPlaceholderText(str(self.gain_const_value))

            except:
                # Gestion erreur
                self.gain_const_value = 1.  # Valeur par défaut en cas d'erreur de conversion
                self.gain_const_entry.clear()
                self.gain_const_entry.setPlaceholderText(str(self.gain_const_value))
            return self.gain_const_value

        self.gain_const_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, update_gain_const_value(), self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        gain_lin_label = QLabel("Gain linéaire")
        label_layout.addWidget(gain_lin_label)

        self.gain_lin_entry = QLineEdit()
        self.gain_lin_entry.setPlaceholderText(str(self.gain_lin_value))
        entry_layout.addWidget(self.gain_lin_entry)

        self.t0_lin_label = QLabel("t0 Profondeur")
        label_layout.addWidget(self.t0_lin_label)

        self.t0_lin_entry = QLineEdit()
        self.t0_lin_entry.setPlaceholderText(str(self.t0_lin_value))
        entry_layout.addWidget(self.t0_lin_entry)

        def update_gain_lin_value():
            """
            Méhode qui met à jour self.gain_lin_value.

            Returns:
                self.gain_const_value: défini le gain linéaire.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.gain_lin_entry)

                # Récupération des valeurs
                self.gain_lin_value = float(self.gain_lin_entry.text())

                # Gestion de cas
                if(self.gain_lin_value < 0.):
                        self.gain_lin_value = 0.
                        self.QLineError(self.gain_lin_entry,"Erreur: gl >=0")
                else:
                    self.gain_lin_entry.setPlaceholderText(str(self.gain_lin_value))

            except:
                # Gestion erreur
                self.gain_lin_value = 0.
                self.gain_lin_entry.setPlaceholderText(str(self.gain_lin_value))
                self.gain_lin_entry.clear()
            return self.gain_lin_value
            
        def update_t0_lin_value():
            """
            Méhode qui met à jour self.t0_lin_value.

            Returns:
                self.t0_lin_value: défini le t0 linéaire.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.t0_lin_entry)
                t0_lin_entry_value = self.t0_lin_entry.text()

                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon_value)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())
                L_mult = [p_max / n_samp, t_max / n_samp, 1]

                # Récupération des valeurs et gestion des erreurs
                if(float(t0_lin_entry_value) / L_mult[yindex] >= 0. and float(t0_lin_entry_value) / L_mult[yindex] <= self.ce_value-self.cb_value):
                    self.t0_lin_value = floor(float(t0_lin_entry_value) / L_mult[yindex])
                    self.t0_lin_entry.setPlaceholderText(str(t0_lin_entry_value))
                else:
                    self.QLineError(self.t0_lin_entry,"Erreur: t0 hors intervalle")
                    self.t0_lin_value = 0
            except:
                # Gestion erreur
                self.t0_lin_value = 0
                self.t0_lin_entry.setPlaceholderText(str(self.t0_lin_value))
                self.t0_lin_entry.clear()
            return self.t0_lin_value

        self.gain_lin_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, update_gain_lin_value(), self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.t0_lin_entry.editingFinished.connect(lambda: self.update_img(update_t0_lin_value(),self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        gain_exp_label = QLabel("Gain exponentiel") #<br><span style='font-size:6pt'>Formule: a*e^(b(x-t0))</span></br><br><span style='font-size:6pt'>b = ln(a)/75</span></br>
        label_layout.addWidget(gain_exp_label)

        self.gain_exp_entry = QLineEdit()
        self.gain_exp_entry.setPlaceholderText(str(self.gain_exp_value))
        entry_layout.addWidget(self.gain_exp_entry)

        self.t0_exp_label = QLabel("t0 Profondeur")
        label_layout.addWidget(self.t0_exp_label)

        self.t0_exp_entry = QLineEdit()
        self.t0_exp_entry.setPlaceholderText(str(self.t0_exp_value))
        entry_layout.addWidget(self.t0_exp_entry)

        def update_gain_exp_value():
            """
            Méhode qui met à jour self.gain_exp_value.

            Returns:
                self.gain_exp_value: défini le gain exponentiel.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.gain_exp_entry)

                # Récupération de la valeur
                self.gain_exp_value = float(self.gain_exp_entry.text())

                # Gestion de cas
                if(self.gain_exp_value < 0.):
                        self.gain_exp_value = 0.
                        self.QLineError(self.gain_exp_entry,"Erreur: ge >=0")
                else:
                    self.gain_exp_entry.setPlaceholderText(str(self.gain_exp_value))

            except:
                # Gestion erreur
                self.gain_exp_value = 0.
                self.gain_exp_entry.setPlaceholderText(str(self.gain_exp_value))
                self.gain_exp_entry.clear()
            return self.gain_exp_value
            
        def update_t0_exp_value():
            """
            Méhode qui met à jour self.t0_exp_value.

            Returns:
                self.t0_exp_value: défini le t0 exponentiel.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.t0_exp_entry)

                # Récupération de la valeur
                t0_exp_entry_value = self.t0_exp_entry.text()

                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon_value)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())
                L_mult = [p_max / n_samp, t_max / n_samp, 1]

                # Gestion des erreurs
                if(float(t0_exp_entry_value) / L_mult[yindex] >= 0. and float(t0_exp_entry_value) / L_mult[yindex] <= self.ce_value-self.cb_value):
                    self.t0_exp_value = floor(float(t0_exp_entry_value) / L_mult[yindex])
                    self.t0_exp_entry.setPlaceholderText(str(t0_exp_entry_value))
                else:
                    self.QLineError(self.t0_exp_entry,"Erreur: t0 hors intervalle")
                    self.t0_exp_value = 0
            except:
                # Gestion erreur
                self.t0_exp_value = 0
                self.t0_exp_entry.setPlaceholderText(str(self.t0_exp_value))
                self.t0_exp_entry.clear()
            return self.t0_exp_value

        self.gain_exp_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, update_gain_exp_value(), self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.t0_exp_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,update_t0_exp_value(), self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        pointer_layout = QVBoxLayout()
        pointer_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        gain_layout.addLayout(pointer_layout)

        pointer_title_layout = QHBoxLayout()
        pointer_title_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        pointer_layout.addLayout(pointer_title_layout)

        pointer_label = QLabel("Pointeur")
        pointer_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        pointer_title_layout.addWidget(pointer_label)

        self.xpointer_label = QLabel()
        self.ypointer_label = QLabel()

        pointer_layout.addWidget(self.xpointer_label)
        pointer_layout.addWidget(self.ypointer_label)

        """
        data_instant_pointer_layout = QHBoxLayout()
        pointer_layout.addLayout(data_instant_pointer_layout)

        self.xpointer_instant_label = QLabel()
        self.ypointer_instant_label = QLabel()
        data_instant_pointer_layout.addWidget(self.xpointer_instant_label)
        data_instant_pointer_layout.addWidget(self.ypointer_instant_label)"""

        # Second onglet: Filtres/Outils

        ######### Filtres #########
        ft_wid_ntb = QWidget()
        treatment_notebook.addTab(ft_wid_ntb, "Filtres/Outils")

        ft_layout = QVBoxLayout(ft_wid_ntb)
        ft_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_ft_layout = QHBoxLayout()
        ft_layout.addLayout(title_ft_layout)
        title_ft_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        filter_title_label = QLabel("Filtres")
        filter_title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_ft_layout.addWidget(filter_title_label)

        self.dewow_button = QPushButton("Dewow")
        self.dewow_button.clicked.connect(self.dewow_butt)
        ft_layout.addWidget(self.dewow_button)

        under_ft_layout = QHBoxLayout()
        ft_layout.addLayout(under_ft_layout)

        uft_label_layout = QVBoxLayout()
        under_ft_layout.addLayout(uft_label_layout)

        uft_entry_layout = QVBoxLayout()
        under_ft_layout.addLayout(uft_entry_layout)

        self.sub_mean_label = QLabel("Traces moyenne (en m)")
        uft_label_layout.addWidget(self.sub_mean_label)

        self.sub_mean_entry = QLineEdit()
        uft_entry_layout.addWidget(self.sub_mean_entry)

        def update_sub_mean():
            """
            Méhode qui met à jour self.sub_mean_value.

            Returns:
                self.sub_mean_value: défini la valeur de sub_mean.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.sub_mean_entry)

                #Récupération de la valeur
                sub_mean = float(self.sub_mean_entry.text())

                n_tr = self.feature[0]
                if(self.def_value != None):
                    d_max = self.def_value
                else:
                    d_max = self.feature[2]
                step_time_acq = self.feature[5]
                xindex = self.Xunit.index(self.abs_unit.currentText())

                L_mult = [d_max / n_tr, step_time_acq, 1]

                # Récupération de la valeur
                if(sub_mean / L_mult[xindex] >= 0. and sub_mean / L_mult[xindex] <= n_tr):
                    self.sub_mean_value = int(sub_mean / L_mult[xindex])
                    self.sub_mean_entry.setPlaceholderText(str(sub_mean))
                else:
                    self.sub_mean_value = None
                    self.QLineError(self.sub_mean_entry,"Erreur: Intervalle")
            except:
                # Gestion erreur
                self.sub_mean_value = None
                self.sub_mean_entry.setPlaceholderText("")
                self.sub_mean_entry.clear()
            return self.sub_mean_value

        self.sub_mean_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, update_sub_mean(), self.cutoff_value, self.sampling_value))

        low_pass_layout = QVBoxLayout()
        ft_layout.addLayout(low_pass_layout)

        low_pass_title_ft_layout = QHBoxLayout()
        low_pass_title_ft_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        low_pass_layout.addLayout(low_pass_title_ft_layout)
        
        low_pass_underlayout = QHBoxLayout()
        low_pass_layout.addLayout(low_pass_underlayout)

        low_pass_label_layout = QVBoxLayout()
        low_pass_underlayout.addLayout(low_pass_label_layout)

        low_pass_entry_layout = QVBoxLayout()
        low_pass_underlayout.addLayout(low_pass_entry_layout)

        low_pass_title = QLabel("Passe bas")
        low_pass_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        low_pass_title_ft_layout.addWidget(low_pass_title)

        cutoff_label =  QLabel("Fr coupure")
        low_pass_label_layout.addWidget(cutoff_label)

        self.cutoff_entry = QLineEdit()
        low_pass_entry_layout.addWidget(self.cutoff_entry)

        sampling_label =  QLabel("Fr échantillonage")
        low_pass_label_layout.addWidget(sampling_label)

        self.sampling_entry = QLineEdit()
        low_pass_entry_layout.addWidget(self.sampling_entry)

        def update_cut_value():
            """
            Méhode qui met à jour self.cutoff_value et self.sampling_value.

            Returns:
                self.cutoff_value: défini la valeur cutoff_value.
                self.sampling_value: défini la valeur sampling_value.
            """
            try:
                # Réinitialisation de l'aspect de l'entrée
                self.reset_style(self.cutoff_entry)
                self.reset_style(self.sampling_entry)

                # Récupération des valeurs
                cutoff_value = float(self.cutoff_entry.text())
                sampling_value = float(self.sampling_entry.text())

                # Gestion des cas
                if(cutoff_value >= 0 and sampling_value >= 0):
                    self.cutoff_value = cutoff_value
                    self.cutoff_entry.setPlaceholderText(str(cutoff_value))

                    self.sampling_value = sampling_value
                    self.sampling_entry.setPlaceholderText(str(sampling_value))
                else:
                    if(cutoff_value < 0):
                        self.QLineError(self.cutoff_entry, "Erreur: fr > 0")
                    else:
                        if(sampling_value < 0):
                            self.QLineError(self.sampling_entry, "Erreur: fr > 0")
            except:
                # Gestion erreur
                self.cutoff_value = None
                self.cutoff_entry.setPlaceholderText("")

                self.sampling_value = None
                self.sampling_entry.setPlaceholderText("")
            return self.cutoff_value, self.sampling_value

        self.cutoff_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, update_cut_value()[0], update_cut_value()[1]))
        self.sampling_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, update_cut_value()[0], update_cut_value()[1]))

        ######### Outils #########
        tools_layout = QVBoxLayout()
        ft_layout.addLayout(tools_layout)

        tools_title_layout = QHBoxLayout()
        tools_title_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        tools_layout.addLayout(tools_title_layout)

        tools_title = QLabel("Outils")
        tools_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        tools_title_layout.addWidget(tools_title)

        under_tools_layout = QHBoxLayout()
        tools_layout.addLayout(under_tools_layout)

        self.inv_button = QPushButton("Inversement")
        self.inv_button.clicked.connect(self.inv_solo)
        under_tools_layout.addWidget(self.inv_button)

        self.eq_button = QPushButton("Égalisation")
        self.eq_button.clicked.connect(self.equalization)
        under_tools_layout.addWidget(self.eq_button)

        # Troisième onglet: Analyse
        analyze_wid_ntb = QWidget()
        treatment_notebook.addTab(analyze_wid_ntb, "Analyse")

        analyze_layout = QVBoxLayout(analyze_wid_ntb)
        analyze_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_mode_layout = QHBoxLayout()
        analyze_layout.addLayout(title_mode_layout)
        title_mode_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        mode_label = QLabel("Mode")
        mode_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_mode_layout.addWidget(mode_label)
        
        point_mode = QPushButton("Mode Point")
        point_mode.clicked.connect(lambda: self.QCanvas.set_mode("Point", point_mode))
        analyze_layout.addWidget(point_mode)

        rectbox_mode = QPushButton("Mode Rectangle")
        rectbox_mode.clicked.connect(lambda: self.QCanvas.set_mode("Rectangle", rectbox_mode))
        analyze_layout.addWidget(rectbox_mode)

        class_layout = QHBoxLayout()
        analyze_layout.addLayout(class_layout)

        class_label = QLabel("Objet:")
        class_layout.addWidget(class_label)

        self.class_choice = QComboBox()
        self.class_choice.addItems([None, "Acier", "Anomalie franche", "Anomalie hétérogène", "Réseaux", "Autres"])
        class_layout.addWidget(self.class_choice)

        self.shape_list = QListWidget()
        analyze_layout.addWidget(self.shape_list)
        self.shape_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.shape_list.customContextMenuRequested.connect(self.QCanvas.del_element)
        
        sidebar_layout.addStretch()

    def select_file(self):
        """
    Méthode permettant de sélectionner un fichier dans la liste des fichiers.
        """
        try:
            # Sélection, chemin et index fichier
            self.selected_file = self.listbox_files.selectedItems()[0].text()
            self.file_index = self.listbox_files.currentRow()
            self.file_path = os.path.join(self.selected_folder, self.selected_file)

            # Création des instances RadarData et RadarController
            self.Rdata = RadarData(self.file_path)
            self.Rcontroller = RadarController()
            
            # Récupération des données de l'image
            self.feature = self.Rdata.get_feature()

            yindex = self.Yunit.index(self.ord_unit.currentText())
            n_samp = self.feature[1]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon_value)) / 2
            L_max = [p_max, t_max, n_samp]
            L_mult = [p_max / n_samp, t_max / n_samp, 1]
            
            # Initialisation de l'entrée découpage début selon l'axe des ordonnées
            self.cb_entry.setPlaceholderText(str(float(self.cb_value)*L_mult[yindex]))

            # Initialisation de la variable et de l'entrée découpage fin selon l'axe des ordonnées
            if(self.cb_entry.text() == ''):
                if(self.ce_entry.text() == ''):
                    self.ce_value = floor(L_max[yindex] / L_mult[yindex])
                    self.ce_entry.setPlaceholderText(str(round(L_max[yindex],2)))

            # Maximum de la liste
            self.max_tr = self.max_list_files()

            # Initialisation de la couleur de la figure
            self.figure.set_facecolor('white')
            # Appelle de la fonction update_img afin de mettre à jour la figure
            self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Erreur Sélection fichier:")
            traceback.print_exc()

    def max_list_files(self):
        """
        Méthode permettant de récupérer le nombre de traces maximal parmis une liste de fichiers.
        """
        # Récupérations des fichiers
        files = [self.listbox_files.item(row).text() for row in range(self.listbox_files.count())]

        # Recherche du maximum
        max = 0
        for file in files:
            file_path = os.path.join(self.selected_folder, file)
            Rdata = RadarData(file_path)
            n_tr = Rdata.get_feature()[0]
            if(max < n_tr):
                max = n_tr
        return max

    def filter_list_file(self):
        """
        Méthode permettant de filtrer la liste de fichiers en fonction du type de fréquence.
        """
        try:
            index = self.freq_state.index(self.filter_button.text()) + 1
            if(index+1 <= len(self.freq_state)):
                self.filter_button.setText(self.freq_state[index])
                self.update_files_list()
            else:
                index = 0
                self.filter_button.setText(self.freq_state[index])
                self.update_files_list()
        except:
            print(f"Aucun dossier sélectionné, filtrage impossible:")
            traceback.print_exc()

    def filter_mult(self):
        """
    Méthode permettant de filtrer la liste de fichier en fonction du format souhaité.
        """
        try:
            index = self.ext_list.index(self.mult_button.text()) + 1
            if(index+1 <= len(self.ext_list)):
                self.mult_button.setText(self.ext_list[index])
                self.update_files_list()
            else:
                index = 0
                self.mult_button.setText(self.ext_list[index])
                self.update_files_list()
        except:
            print(f"Aucun dossier sélectionné, filtrage impossible:")
            traceback.print_exc()

    def inv_file_list(self):
        """
    Méthode inversant certains fichiers afin d'avoir une spacialisation correcte (voir contexte de la prise des données par radar).
        """
        try:
            inv_status = ["off", "on"]
            index = inv_status.index(self.inv_list_state) + 1
            if(index+1 <= len(inv_status)):
                self.inv_list_state = "on"
                self.inv_list_button.setStyleSheet("""     
                QPushButton:active {
                    background-color: #45a049;}""")

                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                self.inv_list_state = "off"
                self.inv_list_button.setStyleSheet("")
                
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv:")
            traceback.print_exc()

    def dewow_butt(self):
        """
    Méthode permettant d'apliquer le filtre dewow à l'aide d'un bouton.
        """
        try:
            dewow_status = ["off", "on"]
            index = dewow_status.index(self.dewow_state) + 1
            if(index+1 <= len(dewow_status)):
                self.dewow_state = "on"
                self.dewow_button.setStyleSheet("""     
                QPushButton:active {
                    background-color: #45a049;}""")

                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                self.dewow_state = "off"
                self.dewow_button.setStyleSheet("")
                
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Dewow:")
            traceback.print_exc()

    def inv_solo(self):
        """
    Méthode permettant d'inverser votre matrice. L'inversion consiste à inverser les colonnes.
        """
        try:
            inv_status = ["off", "on"]
            index = inv_status.index(self.inv_state) + 1
            if(index+1 <= len(inv_status)):
                self.inv_state = "on"
                self.inv_button.setStyleSheet("""     
                QPushButton:active {
                    background-color: #45a049;}""")
                
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                self.inv_state = "off"
                self.inv_button.setStyleSheet("")

                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv_solo:")
            traceback.print_exc()

    def equalization(self):
        """
    Méthode permettant de mettre toutes les images à la même taille en rajoutant des colonnes.
        """
        try:
            eq_status = ["off", "on"]
            index = eq_status.index(self.equal_state) + 1
            if(index+1 <= len(eq_status)):
                self.def_entry.clear()
                self.equal_state = "on"
                self.eq_button.setStyleSheet("""     
                QPushButton:active {
                    background-color: #45a049;}""")
                
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                self.equal_state = "off"
                self.eq_button.setStyleSheet("")

                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Égalisation:")
            traceback.print_exc()

    def radargram(self):
        layout = QVBoxLayout(self.radargram_widget)

        self.canvas = self.QCanvas.canvas
        layout.addWidget(self.canvas)

        # Initialisation des axes x et y. Réglages des axes. Déplacer l'axe des abscisses vers le haut
        self.axes.xaxis.set_ticks_position('top')
        self.axes.xaxis.set_label_position('top')
        self.axes.yaxis.set_ticks_position('left')
        self.axes.yaxis.set_label_position('left')

        self.axes.set_axis_off()


    def update_img(self, t0_lin: int, t0_exp: int, g: float, g_lin: float, g_exp: float, cb: float, ce: float, sub, cutoff: float, sampling: float):
        """
        Méthode qui met à jour notre image avec les différentes applications possibles.

        Args:
            - t0_lin: valeur du début de l'application du gain linéaire.\n
            - t0_exp: valeur du début de l'application du gain exponentiel.\n
            - g: valeur du gain constant.\n
            - g_lin: valeur du gain linéaire.\n
            - g_exp: valeur du gain exponentiel.\n
            - cb: valeur de découpage de début selon l'axe des ordonnées.\n
            - ce: valeur de découpage de fin selon l'axe des ordonnées.\n
            - sub: valeur de de la trace moyenne.\n
            - cutoff: valeur de coupure du passe bas.\n
            - sampling: valeur d'échantillonage.
        """
        try:
            # Récupération de l'image
            self.img = self.Rdata.rd_img()
            
            # Découpage
            self.img_modified = self.img[int(cb):int(ce), :]

            # Application filtre: dewow
            if(self.dewow_state == "on"):
                self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

            # Application filtre: passe-bas
            if(self.cutoff_entry.text() != '' and self.sampling_entry.text() != ''):
                self.img_modified = self.Rcontroller.low_pass(self.img_modified, cutoff, sampling)

            # Application filtre: trace moyenne
            if(sub != None):
                self.img_modified = self.Rcontroller.sub_mean(self.img_modified, sub)

            # Inversement contextuels (inversement pairs)
            if(self.inv_list_state == "on"):
                if(self.file_index % 2 != 0):
                    self.img_modified = np.fliplr(self.img_modified)

            # Inversement
            if(self.inv_state == "on"):
                self.img_modified = np.fliplr(self.img_modified)
            
            # Application des gains
            self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, t0_lin, t0_exp, g, g_lin, g_exp)

            # Égalisation
            if(self.equal_state == "on"):
                if self.img_modified.shape[1] < self.max_tr:
                    # Ajout des colonnes supplémentaires
                    additional_cols = self.max_tr - self.img_modified.shape[1]
                    self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')            

            # Appelle de la fonction update_axes
            self.update_axes(self.def_value, self.epsilon_value)
        except:
            print(f"Erreur dans l'affichage de l'image:")
            traceback.print_exc()

    def update_axes(self, dist: float, epsilon: float):
        """
        Méthode qui met à jour les axes de notre image.

        Args:
            - dist: valeur de la distance définie par l'utilisateur
            - epsilon: valeur de la permittivité.
        """
        try:
            self.update_canvas_image()

            # Données de l'image
            n_tr = self.feature[0]
            n_samp = self.feature[1]
            d_max = self.feature[2]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2
            step_time = self.feature[5]

            # Indexs et conversions des valeurs
            xindex = self.Xunit.index(self.abs_unit.currentText())
            yindex = self.Yunit.index(self.ord_unit.currentText())
            L_xmult = [d_max / n_tr, step_time, 1]
            L_ymult = [p_max / n_samp, t_max / n_samp, 1]
            L_xmax = [d_max, step_time*n_tr, n_tr]

            # Variables axes
            X = []
            Y = []

            if(self.equal_state == "on"):
                X = np.linspace(0.,self.max_tr * L_xmult[xindex],10)
                self.axes.set_xlabel(self.Xlabel[xindex])
                Y = np.linspace(0, (self.ce_value - self.cb_value) * L_ymult[yindex], 10)
                self.axes.set_ylabel(self.Ylabel[yindex])
            else:
                if(dist != None and self.abs_unit.currentText() == "Distance"):
                    X = np.linspace(0.,dist,10)
                    self.axes.set_xlabel(self.Xlabel[xindex])
                else:
                    X = np.linspace(0.,L_xmax[xindex],10)
                    self.axes.set_xlabel(self.Xlabel[xindex])
                Y = np.linspace(0., (self.ce_value - self.cb_value) * L_ymult[yindex], 10)
                self.axes.set_ylabel(self.Ylabel[yindex])

            # Ajouter un titre à la figure
            self.figure.suptitle(self.selected_file[:-4], y = 0.05, va="bottom")

            # Affichage 
            self.axes.imshow(self.img_modified, cmap=self.color.currentText(), interpolation=self.interpolation.currentText(), aspect=self.aspect.currentText(), extent = [X[0],X[-1],Y[-1], Y[0]])
            self.canvas.draw()
            # Supprimer la liste des formes
            self.QCanvas.clear_list()

            # Mise à jours des entrées, labels ...
            self.update_scale_labels(epsilon)
            self.prec_abs = self.abs_unit.currentText()
            self.prec_ord = self.ord_unit.currentText()
        except:
            print(f"Erreur axes:")
            traceback.print_exc()

    def update_scale_labels(self, epsilon: float):
        """
        Méthode qui met à jour les différents labels et modifie les champs non vides pour coïncider avec les valeurs des axes.

        Args:
            - epsilon: valeur de la permittivité
        """
        try:
            # Données sur l'image
            n_tr = self.feature[0]
            n_samp = self.feature[1]
            if(self.def_value != None):
                d_max = self.def_value
            else:
                d_max = self.feature[2]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2
            step_time = self.feature[5]
            antenna = self.feature[6]

            # Indexs et conversions
            xindex = self.Xunit.index(self.abs_unit.currentText())
            yindex = self.Yunit.index(self.ord_unit.currentText())
            L_xmax = [d_max, step_time*n_tr, n_tr]
            L_ymax = [p_max, t_max, n_samp]

            # Visibilité
            if(self.abs_unit.currentText() != "Distance"):
                self.def_label.setVisible(False)
                self.def_entry.setVisible(False)
            else:
                self.def_label.setVisible(True)
                self.def_entry.setVisible(True)

            if(self.ord_unit.currentText() != "Profondeur"):
                self.epsilon_label.setVisible(False)
                self.epsilon_entry.setVisible(False)
            else:
                self.epsilon_label.setVisible(True)
                self.epsilon_entry.setVisible(True)

            # Mettre à jour les yscales
            if(self.epsilon_entry.text() != ''):
                self.epsilon_entry.setPlaceholderText(str(self.epsilon_value))
                self.epsilon_entry.clear()
            else:
                self.epsilon_entry.setPlaceholderText(str(self.epsilon_value))

            if(self.cb_entry.text() != ''):
                if(self.ord_unit.currentText() == "Profondeur"):
                    self.cb_entry.clear()
                    self.cb_entry.setText(str(round((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],2)))
                    self.cb_entry.setPlaceholderText(str(round((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],2)))
                else:
                    cb = ceil((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                    self.cb_entry.clear()
                    self.cb_entry.setText(str(cb))
                    self.cb_entry.setPlaceholderText(str(cb))
            else:
                if(self.prec_ord != self.ord_unit.currentText()):
                    if(self.ord_unit.currentText() == "Profondeur"):
                        self.cb_entry.setPlaceholderText(str(round((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],2)))
                    else:
                        cb = ceil((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                        self.cb_entry.setPlaceholderText(str(cb))

            if(self.ce_entry.text() != ''):
                if(self.ord_unit.currentText() == "Profondeur"):
                    self.ce_entry.clear()
                    self.ce_entry.setText(str(round((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],2)))
                    self.ce_entry.setPlaceholderText(str(round((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],2)))
                else:
                    ce = ceil((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                    self.ce_entry.clear()
                    self.ce_entry.setText(str(ce))
                    self.ce_entry.setPlaceholderText(str(ce))
            else:
                if(self.prec_ord != self.ord_unit.currentText()):
                    if(self.ord_unit.currentText() == "Profondeur"):
                        self.ce_entry.setPlaceholderText(str(round((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],2)))
                    else:
                        ce = ceil((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                        self.ce_entry.setPlaceholderText(str(ce))


            # Mettre à jour les t0
            if(self.t0_lin_entry.text() != '' and (self.prec_ord != self.ord_unit.currentText() or self.cb_entry.text() != '')):
                if(self.ord_unit.currentText() == "Profondeur"):
                    t0_lin_value = round((self.t0_lin_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],1)
                else:
                    t0_lin_value = ceil((self.t0_lin_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_lin_entry.clear()
                self.t0_lin_entry.setText(str(t0_lin_value))
                self.t0_lin_entry.setPlaceholderText(str(t0_lin_value))

            if(self.t0_exp_entry.text() != '' and (self.prec_ord != self.ord_unit.currentText() or self.cb_entry.text() != '')):
                if(self.ord_unit.currentText() == "Profondeur"):
                    t0_exp_value = round((self.t0_exp_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],1)
                else:
                    t0_exp_value = ceil((self.t0_exp_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_exp_entry.clear()
                self.t0_exp_entry.setText(str(t0_exp_value))
                self.t0_exp_entry.setPlaceholderText(str(t0_exp_value))

            if(self.sub_mean_entry.text() != ''):
                if(self.abs_unit.currentText() == "Distance"):
                    sub_mean_value = round((self.sub_mean_value / n_tr) * L_xmax[self.Xunit.index(self.abs_unit.currentText())],1)
                else:
                    sub_mean_value = ceil((self.sub_mean_value / n_tr) * L_xmax[self.Xunit.index(self.abs_unit.currentText())])

                # Efface le contenu actuel de la zone de texte
                self.sub_mean_entry.clear()
                self.sub_mean_entry.setText(str(sub_mean_value))
                self.sub_mean_entry.setPlaceholderText(str(sub_mean_value))

            # Mettre à jour le texte du label
            self.t0_lin_label.setText("t0 " + self.ord_unit.currentText() + ":")
            self.t0_exp_label.setText("t0 " + self.ord_unit.currentText() + ":")

            d_max = self.feature[2]
            L_xmax = [d_max, step_time*n_tr, n_tr]
            self.data_xlabel.setText(self.abs_unit.currentText() + ": {:.2f} {}".format(L_xmax[xindex], self.xLabel[xindex]))
            self.data_ylabel.setText(self.ord_unit.currentText() + ": {:.2f} {}".format(L_ymax[yindex], self.yLabel[yindex]))

            self.ant_radar.setText("Antenne radar: "+antenna)

            if(xindex != 2):
                self.sub_mean_label.setText("Traces moyenne (en "+ str(self.xLabel[xindex])+")")
            else:
                self.sub_mean_label.setText("Traces moyenne")

        except:
            print("Erreur Modification des labels et des entrées:")
            traceback.print_exc()

    def update_canvas_image(self):
        """
        Méthode qui nettoie (efface le contenu dans la figure) et réinitialise la figure.
        """
        # Effacer le contenu existant de la figure
        self.figure.clf()

        # Réinitialiser les axes de la figure
        self.axes = self.figure.add_subplot(111)
        
        self.QCanvas.reset_axes(self.axes, self)

        self.axes.set_xlabel("")
        self.axes.set_ylabel("")

        self.axes.xaxis.set_ticks_position('top')
        self.axes.xaxis.set_label_position('top')
        self.axes.yaxis.set_ticks_position('left')
        self.axes.yaxis.set_label_position('left')

    def QLineError(self, ledit, text: str):
        """
        Méthode appelé en cas d'erreur du domaine de définition d'une variable.

        Args:
            - ledit: l'entrée.
            - text: le texte qui apparaît en cas d'erreur
        """
        ledit.clear()
        ledit.setPlaceholderText(text)
        ledit.setStyleSheet("""     
        QLineEdit {
        background-color: red;
        color: black;}""")

    def reset_style(self, ledit):
        """
        Réinitialise l'entrée.

        Args:
            - ledit: l'entrée
        """
        ledit.setStyleSheet("")

        
if __name__ == '__main__':
    software_name = "NablaPy"
    main_window = MainWindow(software_name)
    main_window.show()