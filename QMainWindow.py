import sys
import traceback
import os
import time
import numpy as np

from RadarController import RadarController
from RadarData import RadarData, cste_global
from math import sqrt, ceil, floor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QListWidget, QPushButton, QScrollArea, QComboBox, QLineEdit, QTabWidget
from PyQt6.QtGui import QAction, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        self.cb_value = 0
        self.ce_value = None
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
        min_height = 775

        # Sidebar
        self.sidebar_widget = QWidget(self.window)

        # Définir la taille limite du sidebar
        self.sidebar_widget.setMinimumHeight(min_height)
        self.sidebar_widget.setFixedWidth(294)



        # Radargram
        self.radargram_widget = QWidget(self.window)

        # Définir la taille limite du radargramme
        self.radargram_widget.setMinimumWidth(600)
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
            if(self.selected_folder != ""):
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
        try:
            folder_path = QFileDialog.getExistingDirectory(self.window, "Sauvegarde des images")
            files = [self.listbox_files.item(row).text() for row in range(self.listbox_files.count())]
            file_index = 0
            prec_selected_file = self.selected_file
            for file in files:
                self.selected_file = file
                file_index += 1
                self.Rdata = RadarData(self.selected_folder + "/"+ file)

                self.update_canvas_image()

                self.img = self.Rdata.rd_img()
                self.img_modified = self.img[int(self.cb_value):int(self.ce_value), :]

                if(self.dewow_button.text() == "Dewow activé"):
                    self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

                if(self.cutoff_entry.text() != '' and self.sampling_entry.text() != ''):
                    self.img_modified = self.Rcontroller.low_pass(self.img_modified, self.cutoff_value, self.sampling_value)

                if(self.sub_mean_value != None):
                    self.img_modified = self.Rcontroller.sub_mean(self.img_modified, self.sub_mean_value)

                if(self.inv_list_button.text() == "Inversement pairs activé"):
                    if(file_index % 2 == 0):
                        self.img_modified = np.fliplr(self.img_modified)

                if(self.inv_button.text() == "Inversement activé"):
                    self.img_modified = np.fliplr(self.img_modified)

                self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)

                if(self.eq_button.text() == "Égalisation activée"):
                    if self.img_modified.shape[1] < self.max_tr:
                        # Ajouter des colonnes supplémentaires
                        additional_cols = self.max_tr - self.img_modified.shape[1]
                        self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')            

                self.update_axes(self.epsilon)

                # Sauvegarder l'image en format PNG
                file_save_path = folder_path + "/" + file + ".png"
                self.figure.savefig(file_save_path)

            # 
            self.selected_file = prec_selected_file
            self.Rdata = RadarData(self.file_path)
            self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Erreur lors de la sauvegarde des images.")
            traceback.print_exc()

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
        self.abs_unit.currentTextChanged.connect(lambda: self.update_axes(self.epsilon))
        display_layout.addWidget(self.abs_unit)

        ord_label = QLabel("Unité en ordonnée")
        display_layout.addWidget(ord_label)

        self.ord_unit = QComboBox()
        self.ord_unit.addItems(["Profondeur", "Temps", "Samples"])
        self.ord_unit.setCurrentText("Profondeur")
        self.ord_unit.currentTextChanged.connect(lambda: self.update_axes(self.epsilon))
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
        notebook.addTab(gain_wid_ntb, "Gains/Outils")

        gain_layout = QVBoxLayout(gain_wid_ntb)
        gain_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

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

        self.gain_const_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, update_gain_const_value(), self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))

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
                        print((float(t0_lin_entry_value) / L_mult[yindex]),self.ce_value-self.cb_value)
                        if((float(t0_lin_entry_value) / L_mult[yindex]) >= 0. and (float(t0_lin_entry_value) / L_mult[yindex]) <= self.ce_value-self.cb_value):
                            self.t0_lin_value = int(float(t0_lin_entry_value) / L_mult[yindex])
                            self.gain_lin_value = float(gain_lin_entry_value)
                        else:
                            print((float(t0_lin_entry_value) / L_mult[yindex]),self.ce_value-self.cb_value)
                            # Efface le contenu actuel de la zone de texte
                            self.t0_lin_entry.clear()
                            # Insère le message d'erreur
                            self.t0_lin_entry.insert("Erreur")

                            self.t0_lin_value = 0
                            self.gain_lin_value = float(gain_lin_entry_value)

                    else:
                        self.t0_lin_value = 0
                        self.gain_lin_value = float(gain_lin_entry_value)

                        
                else:
                    if(t0_lin_entry_value.isdigit() or t0_lin_entry_value.find(".") != -1):
                        if(float(t0_lin_entry_value) / L_mult[yindex] >= 0. and float(t0_lin_entry_value) / L_mult[yindex] <= self.ce_value-self.cb_value):
                            self.t0_lin_value = int(float(t0_lin_entry_value) / L_mult[yindex])
                            self.gain_lin_value = 0.
                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_lin_entry.clear()
                            # Insère le message d'erreur
                            self.t0_lin_entry.insert("Erreur")

                            self.t0_lin_value = 0
                            self.gain_lin_value = 0.

                    else:
                        print("aucune valeur du tout")
                        self.t0_lin_value = 0
                        self.gain_lin_value = 0.

            except:
                traceback.print_exc()
            return self.gain_lin_value, self.t0_lin_value

        self.gain_lin_entry.editingFinished.connect(lambda: self.update_img(update_gain_lin_value()[1],self.t0_exp_value, self.gain_const_value, update_gain_lin_value()[0], self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.t0_lin_entry.editingFinished.connect(lambda: self.update_img(update_gain_lin_value()[1],self.t0_exp_value, self.gain_const_value, update_gain_lin_value()[0], self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))

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
                        if(float(t0_exp_entry_value) / L_mult[yindex] >= 0. and float(t0_exp_entry_value) / L_mult[yindex] <= self.ce_value-self.cb_value):
                            self.t0_exp_value = int(float(t0_exp_entry_value) / L_mult[yindex])
                            self.gain_exp_value = float(gain_exp_entry_value)

                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_exp_entry.clear()
                            # Insère le message d'erreur
                            self.t0_exp_entry.insert("Erreur") 

                            self.t0_exp_value = 0
                            self.gain_exp_value = float(gain_exp_entry_value)

                    else:
                        self.t0_exp_value = 0
                        self.gain_exp_value = float(gain_exp_entry_value)
                        
                else:
                    if(t0_exp_entry_value.isdigit() or t0_exp_entry_value.find(".") != -1):
                        if(float(t0_exp_entry_value) >= 0. and float(t0_exp_entry_value) <= self.ce_value-self.cb_value):
                            self.t0_exp_value = int(float(t0_exp_entry_value) / L_mult[yindex])
                            self.gain_exp_value = 0.

                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_exp_entry.clear() 
                            # Insère le message d'erreur
                            self.t0_exp_entry.insert("Erreur t0") 

                            self.t0_exp_value = 0. 
                            self.gain_exp_value = 0.

                    else:
                        self.t0_exp_value = 0
                        self.gain_exp_value = 0.
            except ValueError:
                traceback.print_exc()
            return self.gain_exp_value, self.t0_exp_value

        self.gain_exp_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, update_gain_exp_value()[1], self.gain_const_value, self.gain_lin_value, update_gain_exp_value()[0], self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.t0_exp_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,update_gain_exp_value()[1], self.gain_const_value, self.gain_lin_value, update_gain_exp_value()[0], self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        tools_layout = QVBoxLayout()
        gain_layout.addLayout(tools_layout)

        tools_title_layout = QHBoxLayout()
        tools_title_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        tools_layout.addLayout(tools_title_layout)

        tools_title = QLabel("Outils")
        tools_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        tools_title_layout.addWidget(tools_title)

        self.inv_button = QPushButton("Inversement désactivé")
        self.inv_button.clicked.connect(self.inv_solo)
        tools_layout.addWidget(self.inv_button)

        self.eq_button = QPushButton("Égalisation désactivée")
        self.eq_button.clicked.connect(self.equalization)
        tools_layout.addWidget(self.eq_button)

        def_layout = QHBoxLayout()
        gain_layout.addLayout(def_layout)

        def_label = QLabel("Définir la Distance:")
        def_layout.addWidget(def_label)

        self.def_entry = QLineEdit()
        def_layout.addWidget(self.def_entry)

        self.def_entry.editingFinished.connect(lambda: self.update_axes(self.epsilon))

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
                if(self.sub_mean_entry.text().isdigit() or self.sub_mean_entry.text().find(".") != -1):
                    n_tr = self.feature[0]
                    if(self.def_entry.text() != ''):
                        d_max = float(self.def_entry.text())
                    else:
                        d_max = self.feature[2]
                    step_time_acq = self.feature[5]
                    xindex = self.Xunit.index(self.abs_unit.currentText())

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
                self.sub_mean_value = None
                self.sub_mean_entry.clear()
                self.sub_mean_entry.insert("Erreur")
                traceback.print_exc()
                return None

        self.sub_mean_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, update_sub_mean(), self.cutoff_value, self.sampling_value))

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
                print("Erreur Trace Moyenne:")
                traceback.print_exc()
                return None

        self.cutoff_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, update_low_pass()[0], update_low_pass()[1]))
        self.sampling_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value,self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, update_low_pass()[0], update_low_pass()[1]))

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
                        if(self.ord_unit.currentText() == "Profondeur"):
                            self.cb_value = ysca1 / L_mult[yindex]
                        else:
                            self.cb_value = ceil(ysca1 / L_mult[yindex])
                else:
                    self.cb_value = 0.
                if(self.ce_entry.text() != ''):
                    ysca2 = float(self.ce_entry.text())
                    if(ysca2 <= L_max[yindex]):
                        if(self.ord_unit.currentText() == "Profondeur"):
                            self.ce_value = ysca2 / L_mult[yindex]
                        else:
                            self.ce_value = ceil(ysca2 / L_mult[yindex])

                else:
                    if(self.ord_unit.currentText() == "Profondeur"):
                        self.ce_value = L_max[yindex] / L_mult[yindex]
                    else:
                        self.ce_value = ceil(L_max[yindex] / L_mult[yindex])
            except:
                print(f"Erreur dans le découpage:")
                traceback.print_exc()
            return self.cb_value, self.ce_value

        self.cb_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, update_cut_value()[0], update_cut_value()[1], self.sub_mean_value, self.cutoff_value, self.sampling_value))
        self.ce_entry.editingFinished.connect(lambda: self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, update_cut_value()[0], update_cut_value()[1], self.sub_mean_value, self.cutoff_value, self.sampling_value))

        title_infos_layout = QVBoxLayout()
        fc_layout.addLayout(title_infos_layout)
        title_infos_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        infos_label = QLabel("Données sur l'image")
        infos_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Use QFont to set the font
        title_infos_layout.addWidget(infos_label)

        self.data_xlabel = QLabel()
        fc_layout.addWidget(self.data_xlabel)

        self.data_ylabel = QLabel()
        fc_layout.addWidget(self.data_ylabel)

        self.ant_radar = QLabel()
        fc_layout.addWidget(self.ant_radar)
        
        sidebar_layout.addStretch()

    def select_file(self):
        """
    Méthode permettant de sélectionner un fichier dans la liste des fichiers.
        """
        try:
            self.selected_file = self.listbox_files.selectedItems()[0].text()
            self.file_index = self.listbox_files.currentRow() # Index du fichier sélectionné
            self.file_path = os.path.join(self.selected_folder, self.selected_file)
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
                if(self.ce_entry.text() == ''):
                    self.ce_value = int(L_max[yindex] / L_mult[yindex])

            self.max_tr = self.max_list_files()
            self.figure.set_facecolor('white')
            self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
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

    def filter_list_file(self):
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
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.inv_list_button.setText(inv_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv:")
            traceback.print_exc()

    def dewow_butt(self):
        """
    Méthode permettant d'apliquer le filtre dewow à l'aide d'un bouton.
        """
        try:
            dewow_status = ["Dewow désactivé", "Dewow activé"]
            index = dewow_status.index(self.dewow_button.text()) + 1
            if(index+1 <= len(dewow_status)):
                self.dewow_button.setText(dewow_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.dewow_button.setText(dewow_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
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
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.inv_button.setText(inv_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
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
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.eq_button.setText(eq_status[index])
                self.update_img(self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.cb_value, self.ce_value, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Égalisation:")
            traceback.print_exc()

    def radargram(self):
        layout = QVBoxLayout(self.radargram_widget)
        self.figure = Figure(figsize=(12, 8), facecolor='none')
        self.canvas_img = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(1,1,1)

        layout.addWidget(self.canvas_img)

        # Initialisation des axes x et y
            # Réglages des axes
            # Déplacer l'axe des abscisses vers le haut
        self.axes.xaxis.set_ticks_position('top')
        self.axes.xaxis.set_label_position('top')
        self.axes.yaxis.set_ticks_position('left')
        self.axes.yaxis.set_label_position('left')

        self.axes.set_axis_off()

        self.canvas_img.setStyleSheet("background-color: transparent;")


    def update_img(self, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float, cb: float, ce: float, sub, cutoff: float, sampling: float):
        """
        Méthode qui met à jour notre image avec les différentes applications possibles.
        """
        start = time.time()
        self.update_canvas_image()
        try:
            self.img = self.Rdata.rd_img()
            self.img_modified = self.img[int(cb):int(ce), :]

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
            
            self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, t0_lin, t0_exp, g, a_lin, a)

            if(self.eq_button.text() == "Égalisation activée"):
                if self.img_modified.shape[1] < self.max_tr:
                    # Ajouter des colonnes supplémentaires
                    additional_cols = self.max_tr - self.img_modified.shape[1]
                    self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')            

            self.update_axes(self.epsilon)

        except:
            print(f"Erreur dans l'affichage de l'image:")
            traceback.print_exc()
        end = time.time()
        #print(f"Durée en seconde de la méthode update_img: {end-start}")

    def update_axes(self, epsilon: float):
        """
        Méthode qui met à jour les axes de notre image.
        """
        try:
            n_tr = self.feature[0]
            n_samp = self.feature[1]
            if(self.def_entry.text() != '' and self.eq_button.text() != "Égalisation activée"):
                d_max = float(self.def_entry.text())
            else:
                d_max = self.feature[2]
                self.def_entry.clear()
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2
            step_time = self.feature[5]

            xindex = self.Xunit.index(self.abs_unit.currentText())
            yindex = self.Yunit.index(self.ord_unit.currentText())
            L_xmax = [d_max, step_time*n_tr, n_tr]
            L_xmult = [d_max / n_tr, step_time, 1]
            L_ymult = [p_max / n_samp, t_max / n_samp, 1]

            X = []
            Y = []

            if(self.eq_button.text() == "Égalisation activée"):
                X = np.linspace(0.,self.max_tr * L_xmult[xindex],10)
                self.axes.set_xlabel(self.Xlabel[xindex])
                Y = np.linspace(0, (self.ce_value - self.cb_value) * L_ymult[yindex], 10)
                self.axes.set_ylabel(self.Ylabel[yindex])
            else:
                if(self.def_entry.text() != '' and self.abs_unit.currentText() == "Distance"):
                    X = np.linspace(0.,float(self.def_entry.text()),10)
                    self.axes.set_xlabel(self.Xlabel[xindex])
                else:
                    X = np.linspace(0.,L_xmax[xindex],10)
                    self.axes.set_xlabel(self.Xlabel[xindex])
                Y = np.linspace(0., (self.ce_value - self.cb_value) * L_ymult[yindex], 10)
                self.axes.set_ylabel(self.Ylabel[yindex])

            # Ajouter un titre à la figure
            self.figure.suptitle(self.selected_file[:-4], y=0.05, va="bottom")
            self.axes.imshow(self.img_modified, cmap="gray", interpolation="nearest", aspect="auto", extent = [X[0],X[-1],Y[-1], Y[0]])
            self.update_scale_labels(epsilon)
            self.canvas_img.draw()

            self.prec_abs = self.abs_unit.currentText()
            self.prec_ord = self.ord_unit.currentText()
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
            if(self.def_entry.text() != ''):
                d_max = float(self.def_entry.text())
            else:
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
                if(self.ord_unit.currentText() == "Profondeur"):
                    cb = round((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],1)
                else:
                    cb = ceil((self.cb_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])

                # Efface le contenu actuel de la zone de texte
                self.cb_entry.clear()

                self.cb_entry.setText(str(cb))

            if(self.ce_entry.text() != '' and self.prec_ord != self.ord_unit.currentText()):
                if(self.ord_unit.currentText() == "Profondeur"):
                    ce = round((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],1)
                else:
                    ce = ceil((self.ce_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.ce_entry.clear()

                self.ce_entry.setText(str(ce))           

            # Mettre à jour les t0
            if(self.t0_lin_entry.text() != '' and (self.prec_ord != self.ord_unit.currentText() or self.cb_entry.text() != '')):
                if(self.ord_unit.currentText() == "Profondeur"):
                    t0_lin_value = round((self.t0_lin_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],1)
                else:
                    t0_lin_value = ceil((self.t0_lin_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_lin_entry.clear()
                self.t0_lin_entry.setText(str(t0_lin_value))

            if(self.t0_exp_entry.text() != '' and (self.prec_ord != self.ord_unit.currentText() or self.cb_entry.text() != '')):
                if(self.ord_unit.currentText() == "Profondeur"):
                    t0_exp_value = round((self.t0_exp_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())],1)
                else:
                    t0_exp_value = ceil((self.t0_exp_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.currentText())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_exp_entry.clear()

                self.t0_exp_entry.setText(str(t0_exp_value))

            if(self.sub_mean_entry.text() != ''):
                if(self.abs_unit.currentText() == "Distance"):
                    sub_mean_value = round((self.sub_mean_value / n_tr) * L_xmax[self.Xunit.index(self.abs_unit.currentText())],1)
                else:
                    sub_mean_value = ceil((self.sub_mean_value / n_tr) * L_xmax[self.Xunit.index(self.abs_unit.currentText())])

                # Efface le contenu actuel de la zone de texte
                self.sub_mean_entry.clear()

                self.sub_mean_entry.setText(str(sub_mean_value))

            # Mettre à jour le texte du label

            self.t0_lin_label.setText("t0 " + self.ord_unit.currentText() + ":")
            self.t0_exp_label.setText("t0 " + self.ord_unit.currentText() + ":")

            d_max = self.feature[2]
            L_xmax = [d_max, step_time*n_tr, n_tr]
            self.data_xlabel.setText(self.abs_unit.currentText() + ": {:.2f} {}".format(L_xmax[xindex], xLabel[xindex]))
            self.data_ylabel.setText(self.ord_unit.currentText() + ": {:.2f} {}".format(L_ymax[yindex], yLabel[yindex]))

            self.ant_radar.setText("Antenne radar: "+antenna)
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
        self.axes.set_xlabel("a")
        self.axes.set_ylabel("b")

        self.axes.xaxis.set_ticks_position('top')
        self.axes.xaxis.set_label_position('top')
        self.axes.yaxis.set_ticks_position('left')
        self.axes.yaxis.set_label_position('left')


        # Obtenir la position et la taille du canvas
        
        """
        canvas_position = self.canvas_img.pos()
        canvas_size = self.canvas_img.size()
        print("Position du canvas:", canvas_position)
        print("Taille du canvas:", canvas_size)"""