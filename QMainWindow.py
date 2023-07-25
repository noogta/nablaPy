import sys
import traceback
import os
import time
import numpy as np
import pyqtgraph as pg

from RadarController import RadarController
from RadarData import RadarData, cste_global
from math import sqrt, ceil
from PyQt6.QtCore import Qt, QRectF, QSizeF, QPointF, QRect, QByteArray
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QListWidget, QPushButton, QScrollArea, QComboBox, QLineEdit, QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QImage, QAction, QFont, QPainter, QPen
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis




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
        self.window.setGeometry(0, 0, 1720, 900)

        # À définir à la fin
        #self.window.setMaximumWidth(QScreen().availableGeometry().width())
        #self.window.setMaximumHeight(QScreen().availableGeometry().height())

        # Placement de la fenêtre au milieu de l'écran
        #self.center_window()

        # Affichage du Menu
        self.ext_list = [".rd7", "rd3", ".DZT"]
        self.freq_state = "Filtrage désactivé"
        self.menu()
        self.main_block()

        self.gain_const_value = 1.
        self.gain_lin_value = 0.
        self.t0_lin_value = 0
        self.gain_exp_value = 0.
        self.t0_exp_value = 0
        self.epsilon = 6.
        self.sub_mean_value = None
        self.cutoff_value = None
        self.sampling_value = None
        self.cb = 0
        self.ce = None
        self.feature = None

        self.Xunit = ["Distance", "Temps", "Traces"]
        self.Yunit = ["Profondeur", "Temps", "Samples"]
        self.Xlabel = ["Distance en m", "Temps en s", "Traces"]
        self.Ylabel = ["Profondeur en m", "Temps en ns", "Samples"]
        self.sidebar()
        self.radargram()

    def show(self):
        # Affichage de la fenêtre
        self.window.show()
        sys.exit(self.app.exec())

    def menu(self):
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

        save_img_action = QAction("Sauvegarder l'image", self.window)
        save_img_action.triggered.connect(self.save)
        file_menu.addAction(save_img_action)

        save_imgs_action = QAction("Sauvegarder les images", self.window)
        save_imgs_action.triggered.connect(self.save_all)
        file_menu.addAction(save_imgs_action)

        quit_action = QAction("Quitter", self.window)
        quit_action.triggered.connect(self.window.close)  # Fermer la fenêtre lorsqu'on clique sur Quitter
        file_menu.addAction(quit_action)

    def main_block(self):
        # Length
        min_height = 750

        # Sidebar
        self.sidebar_widget = QWidget(self.window)

        # Définir la taille limite du sidebar
        self.sidebar_widget.setMinimumHeight(min_height)
        self.sidebar_widget.setMinimumWidth(250)
        self.sidebar_widget.setMaximumWidth(300)

        # Radargram
        self.radargram_widget = QWidget(self.window)

        # Définir la taille limite du radargramme
        #self.radargram_widget.setMinimumWidth(750)
        self.radargram_widget.setMinimumHeight(min_height)

        # Layout horizontal pour placer le sidebar et le radargramm côte à côte
        contents_layout = QHBoxLayout()
        contents_layout.addWidget(self.sidebar_widget)
        contents_layout.addWidget(self.radargram_widget)

        # Layout vertical pour placer le menu en haut et le layout horizontal en bas
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.window.menuBar())
        main_layout.addLayout(contents_layout)

        # Widget central pour contenir le layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.window.setCentralWidget(central_widget)


    def open_folder(self):
        try:
            self.selected_folder = QFileDialog.getExistingDirectory(self.window, "Ouvrir un dossier", directory="/home/cytech/Mesure/Dourdan/Zone 1")
            self.update_files_list()

            # Supprimer le contenu des entrées
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
            self.files_list = os.listdir(self.selected_folder)

            # Trie de la liste
            self.files_list.sort()

            # Suppresion --> Actualisation de la listbox
            self.listbox_files.clear()

            # États/Formats pour le filtrage par fréquence
            state_freq_list = ["Filtrage désactivé", "Haute Fréquence", "Basse Fréquence"]
            format_freq_list = ["", "_1", "_2"]
            index_freq = state_freq_list.index(self.freq_state)

            # États pour le filtrage par format
            index_format = self.ext_list.index(self.mult_button.text())

            # Filtrage selon les différents critères
            for file in self.files_list:
                if (file.endswith(self.ext_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or state_freq_list[index_freq] == "shut"):
                    self.listbox_files.addItem(file)
                else:
                    if self.ext_list[index_format] == "Format":
                        if (file.find(format_freq_list[index_freq]) != -1 or state_freq_list[index_freq] == "shut"):
                            self.listbox_files.addItem(file)
                    else:
                        if (file.endswith(self.ext_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or state_freq_list[index_freq] == "shut"):
                            self.listbox_files.addItem(file)
        except:
            print("Erreur lors de la mise à jour de la liste des fichiers:")
            traceback.print_exc()

    def save(self):
        return
    
    def save_all(self):
        return

    def sidebar(self):
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
        file_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Use QFont to set the font
        title_file_layout.addWidget(file_label)

        list_scroll_area = QScrollArea()
        self.listbox_files = QListWidget()
        list_scroll_area.setWidget(self.listbox_files) 
        list_scroll_area.setWidgetResizable(True)
        self.listbox_files.clicked.connect(self.select_file)
        list_layout.addWidget(list_scroll_area)

        self.filter_button = QPushButton("Filtrage désactivé")
        self.filter_button.clicked.connect(self.filter_list_file)
        list_layout.addWidget(self.filter_button)

        self.mult_button = QPushButton(".rd7")
        self.mult_button.clicked.connect(self.filter_mult)
        list_layout.addWidget(self.mult_button)

        self.inv_list_button = QPushButton("Inversement pairs désactivé")
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
        display_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Use QFont to set the font
        title_display_layout.addWidget(display_label)

        abs_label = QLabel("Unité en abscisse")
        display_layout.addWidget(abs_label)

        self.abs_unit = QComboBox()
        self.abs_unit.addItems(["Distance", "Temps", "Traces"])
        self.abs_unit.setCurrentText("Distance")
        display_layout.addWidget(self.abs_unit)

        ord_label = QLabel("Unité en ordonnée")
        display_layout.addWidget(ord_label)

        self.ord_unit = QComboBox()
        self.ord_unit.addItems(["Profondeur", "Temps", "Samples"])
        self.ord_unit.setCurrentText("Profondeur")
        display_layout.addWidget(self.ord_unit)

        epsilon_layout = QHBoxLayout()
        display_layout.addLayout(epsilon_layout)

        epsilon_label = QLabel("\u03B5 (permitivité):")
        epsilon_label.setFont(QFont("Arial", 12))  # Use QFont to set the font
        epsilon_layout.addWidget(epsilon_label)

        epsilon_entry = QLineEdit()
        epsilon_layout.addWidget(epsilon_entry)

        def update_epsilon_value():
            try:
                self.epsilon = float(epsilon_entry.text())
                if(self.epsilon <= 0.):
                    self.epsilon = 6.
                    print("La permitivité ne peut être inférieure ou égale 0 !")
            except:
                self.epsilon = 6.
                print("Aucune valeur de epsilon a été définie")
            return self.epsilon
        
        epsilon_entry.editingFinished.connect(lambda: self.update_axes(update_epsilon_value()))

        # Troisième bloc: Outils
        tool_frame = QFrame()
        sidebar_layout.addWidget(tool_frame)


        tool_layout = QVBoxLayout(tool_frame)

        notebook = QTabWidget()
        tool_layout.addWidget(notebook)

        # Premier onglet: Gains/Filtres
        gain_wid_ntb = QWidget()
        notebook.addTab(gain_wid_ntb, "Gains/Infos")

        gain_layout = QVBoxLayout(gain_wid_ntb)
        title_gain_layout = QVBoxLayout()
        gain_layout.addLayout(title_gain_layout)
        title_gain_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        gain_label = QLabel("Gains")
        gain_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Use QFont to set the font
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
        entry_layout.addWidget(self.gain_const_entry)

        def update_gain_const_value():
            try:
                gain_const_value = float(self.gain_const_entry.text())
                if(gain_const_value >= 0.):
                    self.gain_const_value = gain_const_value
            except:
                self.gain_const_value = 1.  # Valeur par défaut en cas d'erreur de conversion
            return self.gain_const_value

        self.gain_const_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, update_gain_const_value(), self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        gain_lin_label = QLabel("Gain linéaire <br><span style='font-size:8pt'>Formule: a(x-t0)</span></br>")
        label_layout.addWidget(gain_lin_label)

        self.gain_lin_entry = QLineEdit()
        entry_layout.addWidget(self.gain_lin_entry)

        self.t0_lin_label = QLabel("t0 Profondeur")
        label_layout.addWidget(self.t0_lin_label)

        self.t0_lin_entry = QLineEdit()
        entry_layout.addWidget(self.t0_lin_entry)

        def update_gain_lin_value():
            try:
                gain_lin_entry_value = self.gain_lin_entry.text()
                t0_lin_entry_value = self.t0_lin_entry.text()
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())
                
                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                if(gain_lin_entry_value.isdigit() or gain_lin_entry_value.find(".") != -1):
                    if(t0_lin_entry_value.isdigit() or t0_lin_entry_value.find(".") != -1):
                        if(float(t0_lin_entry_value) / L_mult[yindex] >= self.cb and float(t0_lin_entry_value) / L_mult[yindex] <= self.ce):
                            self.t0_lin_value = int(float(t0_lin_entry_value) / L_mult[yindex])
                            self.gain_lin_value = float(gain_lin_entry_value)
                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_lin_entry.clear()
                            # Insère le message d'erreur
                            self.t0_lin_entry.insert("Erreur")

                            self.t0_lin_value = int(self.cb)
                            self.gain_lin_value = float(gain_lin_entry_value)

                    else:
                        self.t0_lin_value = int(self.cb)
                        self.gain_lin_value = float(gain_lin_entry_value)

                        
                else:
                    if(t0_lin_entry_value.isdigit() or t0_lin_entry_value.find(".") != -1):
                        if(float(t0_lin_entry_value) / L_mult[yindex] >= self.cb and float(t0_lin_entry_value) / L_mult[yindex] <= self.ce):
                            self.t0_lin_value = int(float(t0_lin_entry_value) / L_mult[yindex])
                            self.gain_lin_value = 0.
                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_lin_entry.clear()
                            # Insère le message d'erreur
                            self.t0_lin_entry.insert("Erreur")

                            self.t0_lin_value = int(self.cb)
                            self.gain_lin_value = 0.

                    else:
                        self.t0_lin_value = int(self.cb)
                        self.gain_lin_value = 0.

            except:
                traceback.print_exc()
            return self.gain_lin_value, self.t0_lin_value

        self.gain_lin_entry.editingFinished.connect(lambda: self.update_img(update_gain_lin_value()[1],self.t0_exp_entry, self.gain_const_value, update_gain_lin_value()[0], self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.t0_lin_entry.editingFinished.connect(lambda: self.update_img(update_gain_lin_value()[1],self.t0_exp_entry, self.gain_const_value, update_gain_lin_value()[0], self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        gain_exp_label = QLabel("Gain exponentiel <br><span style='font-size:8pt'>Formule: e^(a(x-t0))-1</span></br>")
        label_layout.addWidget(gain_exp_label)

        self.gain_exp_entry = QLineEdit()
        entry_layout.addWidget(self.gain_exp_entry)

        self.t0_exp_label = QLabel("t0 Profondeur")
        label_layout.addWidget(self.t0_exp_label)

        self.t0_exp_entry = QLineEdit()
        entry_layout.addWidget(self.t0_exp_entry)

        def update_gain_exp_value():
            try:
                gain_exp_entry_value = self.gain_exp_entry.text()
                t0_exp_entry_value = self.t0_exp_entry.text()
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())

                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                if(gain_exp_entry_value.isdigit() or gain_exp_entry_value.find(".") != -1):
                    if(t0_exp_entry_value.isdigit() or t0_exp_entry_value.find(".") != -1):
                        if(float(t0_exp_entry_value) / L_mult[yindex] >= self.cb and float(t0_exp_entry_value) / L_mult[yindex] <= self.ce):
                            self.t0_exp_value = int(float(t0_exp_entry_value) / L_mult[yindex])
                            self.gain_exp_value = float(gain_exp_entry_value)

                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_exp_entry.clear()
                            # Insère le message d'erreur
                            self.t0_exp_entry.insert("Erreur") 

                            self.t0_exp_value = int(self.cb)
                            self.gain_exp_value = float(gain_exp_entry_value)

                    else:
                        self.t0_exp_value = int(self.cb)
                        self.gain_exp_value = float(gain_exp_entry_value)
                        
                else:
                    if(t0_exp_entry_value.isdigit() or t0_exp_entry_value.find(".") != -1):
                        if(float(t0_exp_entry_value) >= self.cb and float(t0_exp_entry_value) <= self.ce):
                            self.t0_exp_value = int(float(t0_exp_entry_value) / L_mult[yindex])
                            self.gain_exp_value = 0.

                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_exp_entry.clear() 
                            # Insère le message d'erreur
                            self.t0_exp_entry.insert("Erreur t0") 

                            self.t0_exp_value = int(self.cb)
                            self.gain_exp_value = 0.

                    else:
                        self.t0_exp_value = int(self.cb)
                        self.gain_exp_value = 0.
            except ValueError:
                traceback.print_exc()
            return self.gain_exp_value, self.t0_exp_value

        self.gain_exp_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, update_gain_exp_value()[1], self.gain_const_value, self.gain_lin_value, update_gain_exp_value()[0], self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.t0_exp_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        title_infos_layout = QVBoxLayout()
        gain_layout.addLayout(title_infos_layout)
        title_infos_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        infos_label = QLabel("Données sur l'image")
        infos_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Use QFont to set the font
        title_infos_layout.addWidget(infos_label)

        self.data_xlabel = QLabel()
        gain_layout.addWidget(self.data_xlabel)

        self.data_ylabel = QLabel()
        gain_layout.addWidget(self.data_ylabel)

        self.ant_radar = QLabel()
        gain_layout.addWidget(self.ant_radar)

        # Second onglet
        fc_wid_ntb = QWidget()
        notebook.addTab(fc_wid_ntb, "Filtres/Découpage")

        fc_layout = QVBoxLayout(fc_wid_ntb)
        fc_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_fc_layout = QHBoxLayout()
        fc_layout.addLayout(title_fc_layout)
        title_fc_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        filter_title_label = QLabel("Filtres")
        filter_title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Use QFont to set the font
        title_fc_layout.addWidget(filter_title_label)

        self.dewow_button = QPushButton("Dewow désactivé")
        self.dewow_button.clicked.connect(self.dewow_butt)
        fc_layout.addWidget(self.dewow_button)

        under_fc_layout = QHBoxLayout()
        fc_layout.addLayout(under_fc_layout)

        ufc_label_layout = QVBoxLayout()
        under_fc_layout.addLayout(ufc_label_layout)

        ufc_entry_layout = QVBoxLayout()
        under_fc_layout.addLayout(ufc_entry_layout)

        sub_mean_label = QLabel("Traces moyenne")
        ufc_label_layout.addWidget(sub_mean_label)

        self.sub_mean_entry = QLineEdit()
        ufc_entry_layout.addWidget(self.sub_mean_entry)

        def update_sub_mean():
            try:
                event = None
                if(self.sub_mean_entry.text().isdigit() or self.sub_mean_entry.text().find(".") != -1):
                    n_tr = self.feature[0]
                    d_max = self.feature[2]
                    step_time_acq = self.feature[5]
                    xindex = self.Xunit.index(self.abs_unit.text())

                    L_mult = [d_max / n_tr, step_time_acq, 1]
                    if(int(float(self.sub_mean_entry.text()) / L_mult[xindex]) >= 0. and int(float(self.sub_mean_entry.text()) / L_mult[xindex]) <= n_tr):
                        self.sub_mean_value = int(float(self.sub_mean_entry.text()) / L_mult[xindex])
                    else:
                        self.sub_mean_value = None
                        self.sub_mean_entry.clear()
                        self.sub_mean_entry.insert("Erreur")
                else:
                    self.sub_mean_value = None
                    self.sub_mean_entry.clear()
                return self.sub_mean_value
            except:
                print("Erreur Trace moyenne:")
                traceback.print_exc()
                return None

        self.sub_mean_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, update_sub_mean(), self.cutoff_value, self.sampling_value))

        low_pass_layout = QVBoxLayout()
        fc_layout.addLayout(low_pass_layout)

        low_pass_title_fc_layout = QHBoxLayout()
        low_pass_title_fc_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        low_pass_layout.addLayout(low_pass_title_fc_layout)
        
        low_pass_underlayout = QHBoxLayout()
        low_pass_layout.addLayout(low_pass_underlayout)

        low_pass_label_layout = QVBoxLayout()
        low_pass_underlayout.addLayout(low_pass_label_layout)

        low_pass_entry_layout = QVBoxLayout()
        low_pass_underlayout.addLayout(low_pass_entry_layout)

        low_pass_title = QLabel("Passe bas")
        low_pass_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        low_pass_title_fc_layout.addWidget(low_pass_title)

        cutoff_label =  QLabel("Fr coupure")
        low_pass_label_layout.addWidget(cutoff_label)

        self.cutoff_entry = QLineEdit()
        low_pass_entry_layout.addWidget(self.cutoff_entry)

        sampling_label =  QLabel("Fr échantillonage")
        low_pass_label_layout.addWidget(sampling_label)

        self.sampling_entry = QLineEdit()
        low_pass_entry_layout.addWidget(self.sampling_entry)

        def update_low_pass():
            try:
                if((self.cutoff_entry.text().isdigit() or self.cutoff_entry.text().find(".") != -1) and (self.sampling_entry.text().isdigit() or self.sampling_entry.text().find(".") != -1)):
                        cutoff_value = float(self.cutoff_entry.text())
                        sampling_value = float(self.sampling_entry.text())
                        if(cutoff_value >= 0 and sampling_value >= 0):
                            self.cutoff_value = cutoff_value
                            self.sampling_value = sampling_value
                        else:
                            self.cutoff_entry.clear()
                            self.cutoff_entry.insert("Erreur")

                            self.sampling_entry.clear()
                            self.sampling_entry.insert("Erreur")
                else:
                    self.cutoff_value = None
                    self.sampling_value = None

                return self.cutoff_value, self.sampling_value
            except:
                print("Erreur Trace moyenne:")
                traceback.print_exc()
                return None

        self.cutoff_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, update_low_pass()[0], update_low_pass()[1]))
        self.sampling_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, update_low_pass()[0], update_low_pass()[1]))

        cut_layout = QVBoxLayout()
        fc_layout.addLayout(cut_layout)

        cut_title_fc_layout = QHBoxLayout()
        cut_title_fc_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        cut_layout.addLayout(cut_title_fc_layout)
        
        cut_underlayout = QHBoxLayout()
        cut_layout.addLayout(cut_underlayout)

        cut_label_layout = QVBoxLayout()
        cut_underlayout.addLayout(cut_label_layout)

        cut_entry_layout = QVBoxLayout()
        cut_underlayout.addLayout(cut_entry_layout)

        cut_title = QLabel("Découpage")
        cut_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        cut_title_fc_layout.addWidget(cut_title)

        cb_label =  QLabel("Début")
        cut_label_layout.addWidget(cb_label)

        self.cb_entry = QLineEdit()
        cut_entry_layout.addWidget(self.cb_entry)

        ce_label =  QLabel("Fin")
        cut_label_layout.addWidget(ce_label)

        self.ce_entry = QLineEdit()
        cut_entry_layout.addWidget(self.ce_entry)

        def update_cut_value():
            try:
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                yindex = self.Yunit.index(self.ord_unit.currentText())

                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                L_max = [p_max, t_max, n_samp]
                if(self.cb_entry.text() != ''):
                    ysca1 = float(self.cb_entry.text())
                    if(ysca1 >= 0.):
                        self.cb = ysca1 / L_mult[yindex]
                else:
                    self.cb = 0.
                if(self.ce_entry.text() != ''):
                    ysca2 = float(self.ce_entry.text())
                    if(ysca2 <= L_max[yindex]):
                        self.ce = ysca2 / L_mult[yindex]
                else:
                    self.ce = L_max[yindex] / L_mult[yindex]
            except:
                print(f"Erreur dans le découpage:")
                traceback.print_exc()
            return self.cb, self.ce

        self.cb_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, update_cut_value()[0], update_cut_value()[1], self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.ce_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_entry, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, update_cut_value()[0], update_cut_value()[1], self.sub_mean_value, self.cutoff_value, self.sampling_value))

        tools_layout = QVBoxLayout()
        fc_layout.addLayout(tools_layout)

        tools_title_fc_layout = QHBoxLayout()
        tools_title_fc_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        tools_layout.addLayout(tools_title_fc_layout)

        tools_title = QLabel("Outils")
        tools_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        tools_title_fc_layout.addWidget(tools_title)

        self.inv_button = QPushButton("Inversement désactivé")
        self.inv_button.clicked.connect(self.inv_solo)
        tools_layout.addWidget(self.inv_button)

        self.eq_button = QPushButton("Égalisation désactivée")
        self.eq_button.clicked.connect(self.equalization)
        tools_layout.addWidget(self.eq_button)
        
        sidebar_layout.addStretch()

    def select_file(self):
        """
    Méthode permettant de sélectionner un fichier dans la liste des fichiers.
        """
        try:
            selected_file = self.listbox_files.selectedItems()[0].text()
            self.file_index = self.listbox_files.currentRow # Index du fichier sélectionné
            self.file_path = os.path.join(self.selected_folder, selected_file)
            self.Rdata = RadarData(self.file_path)
            self.Rcontroller = RadarController()
            self.feature = self.Rdata.get_feature()

            yindex = self.Yunit.index(self.ord_unit.currentText())
            n_samp = self.feature[1]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2
            L_max = [p_max, t_max, n_samp]
            L_mult = [p_max / n_samp, t_max / n_samp, 1]

            if(self.cb_entry.text() == ''):
                self.ce = int(L_max[yindex] / L_mult[yindex])

            self.max_tr = self.max_list_files()
            self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Erreur Sélection fichier:")
            traceback.print_exc()

    def max_list_files(self):
        """
    Méthode permettant de récupérer le nombre de traces maximal parmis une liste de fichiers.
        """
        files = [self.listbox_files.item(row).text() for row in range(self.listbox_files.count())]
        max = 0
        for file in files:
            file_path = os.path.join(self.selected_folder, file)
            Rdata = RadarData(file_path)
            n_tr = Rdata.get_feature()[0]
            if(max < n_tr):
                max = n_tr
        return max

    def filter_list_file(self, ):
        """
    Méthode permettant de filtrer la liste de fichiers en fonction du type de fréquence.
        """
        try:
            name_freq_list = ["Filtrage désactivé", "Haute Fréquence", "Basse Fréquence"]
            index = name_freq_list.index(self.filter_button.text()) + 1
            if(index+1 <= len(name_freq_list)):
                self.filter_button.setText(name_freq_list[index])
                self.freq_state = name_freq_list[index]
                self.update_files_list()
            else:
                index = 0
                self.filter_button.setText(name_freq_list[index])
                self.freq_state = name_freq_list[index]
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
            inv_status = ["Inversement pairs désactivé", "Inversement pairs activé"]
            index = inv_status.index(self.inv_list_button.text()) + 1
            if(index+1 <= len(inv_status)):
                self.inv_list_button.setText(inv_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.inv_list_button.setText(inv_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv:")
            traceback.print_exc()

    def dewow_butt(self):
        """
    Méthode permettant d'apliquer le filtre dewow à l'aide d'un bouton.
        """
        try:
            dewow_status = ["Dewow désactivé", "Dewow activé"]
            index = dewow_status.index(self.dewow_button_text) + 1
            if(index+1 <= len(dewow_status)):
                self.dewow_button.setText(dewow_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.dewow_button.setText(dewow_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Dewow:")
            traceback.print_exc()

    def inv_solo(self):
        """
    Méthode permettant d'inverser votre matrice. L'inversion consiste à inverser les colonnes.
        """
        try:
            inv_status = ["Inversement désactivé", "Inversement activé"]
            index = inv_status.index(self.inv_button.text()) + 1
            if(index+1 <= len(inv_status)):
                self.inv_button.setText(inv_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.inv_button.setText(inv_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv_solo:")
            traceback.print_exc()

    def equalization(self):
        """
    Méthode permettant de mettre toutes les images à la même taille en rajoutant des colonnes.
        """
        try:
            eq_status = ["Égalisation désactivée", "Égalisation activée"]
            index = eq_status.index(self.eq_button.text()) + 1
            if(index+1 <= len(eq_status)):
                self.eq_button.setText(eq_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.eq_button.setText(eq_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb, self.ce, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Égalisation:")
            traceback.print_exc()

    def radargram(self):
        layout = QVBoxLayout(self.radargram_widget)
        self.radar_window = QMainWindow()
        self.view = QGraphicsView(self.radar_window)
        layout.addWidget(self.view)

        # Create the QGraphicsScene and set it to the view
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        # Initialize the QGraphicsPixmapItem to hold the radar image
        self.radar_image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.radar_image_item)

    def update_img(self, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float, yscale1: float, yscale2: float, sub: int, cutoff: float, sampling: float):
        """
        Méthode qui met à jour notre image avec les différentes applications possibles.
        """
        start = time.time()
        try:
            self.img = self.Rdata.rd_img()
            self.img_modified = self.img[int(yscale1):int(yscale2), :]
            self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, t0_lin - int(yscale1), t0_exp - int(yscale2), g, a_lin, a)

            if(self.dewow_button.text() == "Dewow activé"):
                self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

            if(self.cutoff_entry.text() != '' and self.sampling_entry.text() != ''):
                self.img_modified = self.Rcontroller.low_pass(self.img_modified, cutoff, sampling)

            if(sub != None):
                self.img_modified = self.Rcontroller.sub_mean(self.img_modified, sub)

            if(self.inv_list_button.text() == "Inversement pairs activé"):
                if(self.file_index % 2 != 0):
                    self.img_modified = np.fliplr(self.img_modified)

            if(self.inv_button.text() == "Inversement activé"):
                self.img_modified = np.fliplr(self.img_modified)

            if(self.eq_button.text() == "Égalisation activée"):
                if self.img_modified.shape[1] < self.max_tr:
                    # Ajouter des colonnes supplémentaires
                    additional_cols = self.max_tr - self.img_modified.shape[1]
                    self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')

            # Convertir l'image numpy en QImage
            height, width = self.img_modified.shape
            bytes_per_line = width
            format_ = QImage.Format.Format_Grayscale8
            qimage = QImage(QByteArray(self.img_modified.tobytes()), width, height, bytes_per_line, format_)

            pixmap = QPixmap.fromImage(qimage)

            # Mettre à jour l'image dans radar_image_item
            self.radar_image_item.setPixmap(pixmap)             

            self.update_axes(self.epsilon)

        except:
            print(f"Erreur dans l'affichage de l'image:")
            traceback.print_exc()
        end = time.time()
        print(f"Durée en seconde de la méthode update_img: {end-start}")

    def update_axes(self, epsilon: float):
        """
        Méthode qui met à jour les axes de notre image.
        """
        try:
            n_tr = self.feature[0]
            n_samp = self.feature[1]
            d_max = self.feature[2]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2
            step_time = self.feature[5]

            xindex = self.Xunit.index(self.abs_unit.currentText())
            yindex = self.Yunit.index(self.ord_unit.currentText())
            L_xmax = [d_max, step_time * n_tr, n_tr]
            L_xmult = [d_max / n_tr, step_time, 1]
            L_ymult = [p_max / n_samp, t_max / n_samp, 1]

            X = []
            Y = []

            if(self.eq_button.text() == "Égalisation activée"):
                X = np.linspace(0., self.max_tr * L_xmult[xindex], 10)
                self.view.setLabel('bottom', text=self.Xlabel[xindex])
                Y = np.linspace(self.cb * L_ymult[yindex], self.ce * L_ymult[yindex], 10)
                self.view.setLabel('left', text=self.Ylabel[yindex])

            else:
                X = np.linspace(0., L_xmax[xindex], 10)
                self.view.setLabel('bottom', text=self.Xlabel[xindex])
                Y = np.linspace(self.cb * L_ymult[yindex], self.ce * L_ymult[yindex], 10)
                self.view.setLabel('left', text=self.Ylabel[yindex])

            #self.plot.clear()
            # Notez que nous n'avons plus besoin de self.plot ici, car nous mettons à jour les axes de self.view.
            image_item = pg.ImageItem(self.img_modified)
            self.view.addItem(image_item)
            image_item.setRect(QRectF(X[0], Y[0], X[-1] - X[0], Y[-1] - Y[0]))
            self.view.setRange(xRange=[X[0], X[-1]], yRange=[Y[0], Y[-1]], padding=0)

            self.view.repaint()

            self.prec_abs = self.abs_unit.currentText()
            self.prec_ord = self.ord_unit.currentText()

            self.update_scale_labels(self.epsilon)
        except:
            print(f"Erreur axes:")
            traceback.print_exc()

    def update_scale_labels(self, epsilon: float):
        """
    Méthode qui met à jour les différents labels et modifie les champs non vides pour coïncider avec les valeurs des axes.
        """
        try:
            n_tr = self.feature[0]
            n_samp = self.feature[1]
            d_max = self.feature[2]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2
            step_time = self.feature[5]
            antenna = self.feature[6]

            xLabel = ["m", "s", "mesures"]
            yLabel = ["m", "ns", "samples"]

            xindex = self.Xunit.index(self.abs_unit.currentText())
            yindex = self.Yunit.index(self.ord_unit.currentText())
            L_xmax = [d_max, step_time*n_tr, n_tr]
            L_ymax = [p_max, t_max, n_samp]

            # Mettre à jour les yscales
            if(self.cb_entry.text() != '' and self.prec_ord != self.ord_unit.currentText()):
                yscale1 = ceil((self.cb / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])

                # Efface le contenu actuel de la zone de texte
                self.cb_entry.clear()

                self.cb_entry.setText(str(yscale1))

            if(self.ce_entry.text() != '' and self.prec_ord != self.ord_unit.currentText()):
                if(self.ord_unit.currentText() == "Samples"):
                    yscale2 = ceil((self.ce / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                else:
                    yscale2 = (self.ce / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())]
                
                # Efface le contenu actuel de la zone de texte
                self.ce_entry.clear()

                self.ce_entry.setText(str(yscale2))           

            # Mettre à jour les t0
            if(self.t0_lin_entry.text() != '' and self.prec_ord != self.ord_unit.currentText()):
                t0_lin_value = ceil((self.t0_lin_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_lin_entry.clear()

                self.t0_lin_entry.setText(str(t0_lin_value))

            if(self.t0_exp_entry.text() != '' and self.prec_ord != self.ord_unit.currentText()):
                t0_exp_value = ceil((self.t0_exp_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_exp_entry.clear()

                self.t0_exp_entry.setText(str(t0_exp_value))

            # Mettre à jour le texte du label

            self.t0_lin_label.setText("t0" + self.ord_unit.currentText() + ":")
            self.t0_exp_label.setText("t0" + self.ord_unit.currentText() + ":")

            self.data_xlabel.setText(self.abs_unit.currentText() + ": {:.2f} {}".format(L_xmax[xindex], xLabel[xindex]))
            self.data_ylabel.setText(self.ord_unit.currentText() + ": {:.2f} {}".format(L_ymax[yindex], yLabel[yindex]))

            self.ant_radar.setText("Antenne radar: "+antenna)
        except:
            print("Erreur Modification des labels et des entrées:")
            traceback.print_exc()
"""
if __name__ == "__main__":
    software_name = "NablaPy"
    main_window = MainWindow(software_name)
    main_window.show()"""