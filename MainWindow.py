# ajout des axes sauvegarde # trace moyenne # différent type d'interpolation # Inversement # Même Taille
import tkinter as tk 
from RadarData import RadarData
from RadarData import cste_global
from RadarController import RadarController
from tkinter import filedialog as fd
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
from math import sqrt, ceil
import traceback
import time

class MainWindow():
    """Cette classe représente la fenêtre principale."""
    def __init__(self, appname: str):
        """
        Constructeur de la classe MainWindow.

        Args:
                appname (str): Nom de l'application
                data:
                controller:
                window (Object from tk.Tk) : Fenêtre principale
                title (string): Nom de l'application
                posX (int): Position selon l'axe x de notre application
                posY (int): Position selon l'axe y de notre application
                per_sidebar (int): Pourcentage de la longueur de la barre latérale
        """
        # Création de notre fenêtre principale
        self.window = tk.Tk()
        self.window.title(appname)

        # Placement de la fenêtre au mileu de l'écran
        self.posX = (int(self.window.winfo_screenwidth()) // 2 ) - (1400 // 2) # positionnement x sur l'écran
        self.posY = (int(self.window.winfo_screenheight()) // 2 ) - (self.window.winfo_screenheight() // 2) # positionnement y sur l'écran

        # Geométrie de la fenêtre
        self.window.geometry("{}x{}+{}+{}".format(1400, self.window.winfo_screenheight(),self.posX,self.posY))
        self.window.update()
        
        # Création des instances
        self.Rdata = RadarData()
        # Initiation de file_path
        self.file_path = ""
        # Affichage des différentes parties et création des variables
            # Menu
        self.img = None
        self.img_modified = None
        self.file_list_sort = list[str]
        self.menu()

            # Frame principale
        self.window_frame = tk.Frame(self.window)
        self.window_frame.pack(fill="both", expand=True)

            # Barre de contrôle
                # État initial du filtre des fichiers
        self.list_ext = [".rd7" ,".rd3", ".DZT", "Format"]
        self.freq_state = "shut"

                # Définition des valeurs des gains
        self.gain_const_value = 1.
        self.gain_lin_value = 0.
        self.t0_lin_value = 0
        self.gain_exp_value = 0.
        self.t0_exp_value = 0
        self.epsilon = 6. # cas dans le vide (Impossible)
        self.sub_mean_value = None
        self.cutoff_value = None
        self.sampling_value = None

        self.Xunit = ["Distance", "Temps", "Traces"]
        self.Yunit = ["Profondeur", "Temps", "Samples"]
        self.Xlabel = ["Distance en m", "Temps en s", "Traces"]
        self.Ylabel = ["Profondeur en m", "Temps en ns", "Samples"]
        self.feature = None

        self.sidebar(self.window_frame)

            # Radargramme
        self.figure = None

        self.ysca1 = 0.
        self.ysca2 = None
        self.radargram(self.window_frame)

    def menu(self):
        """Méthode qui crée le menu de notre application"""
        # Création du Menu
        menu_bar = tk.Menu(self.window)
        self.menu_bar = menu_bar
        self.window.config(menu=self.menu_bar)

        # Création du sous-menu File
        file_menu = tk.Menu(menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir un dossier", command=self.open_menu_command)
        file_menu.add_command(label="Sauvegarder", command=self.save)
        file_menu.add_command(label="Sauvegarder les fichiers", command=self.save_all)
        file_menu.add_command(label="Quitter", command=self.window.quit)

        # Création du sous-menu Edit
        edit_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Modifier", menu=edit_menu)

        """
        En contruction:
        file_menu.add_command(label="Open", command=self.file_menu_command)
        file_menu.add_command(label="Exit", command=self.quit)
        """

        # Création du sous-menu View
        view_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Fenêtre", menu=view_menu)

    ### Menu --> Fichier ###
    def open_menu_command(self):
        try:
            self.selected_directory = fd.askdirectory(initialdir="")
            self.update_file_list()
            self.yscale1.delete('0', 'end')
            self.yscale2.delete('0', 'end')
        except:
            print(f"Erreur lors de la sélection du dossier:")
            traceback.print_exc()


    def update_file_list(self):
        """
    Méthode qui met à jour la liste des fichiers du logiciel.
        """
        # Création de la variable de type list str, self.file_list
        try:
            self.file_list = os.listdir(self.selected_directory)

            # Trie de la liste
            self.file_list.sort()

            # Suppresion --> Actualisation de la listbox
            self.listbox_files.delete(0, tk.END)

            # États/Formats pour le filtrage par fréquence
            state_freq_list = ["shut", "high", "low"]
            format_freq_list = ["", "_1", "_2"]
            index_freq = state_freq_list.index(self.freq_state)
            
            # États pour le filtrage par format
            state_format_list = self.list_ext
            index_format = state_format_list.index(self.mult_button_text.get())

            # Filtrage selon les différents critères
            for file in self.file_list:
                if((file.endswith(state_format_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or state_freq_list[index_freq] == "shut" )):
                    self.listbox_files.insert(tk.END, file)
                    #self.file_list_sort.append(file)
                else:
                    if state_format_list[index_format] == "Format":
                        if((file.find(format_freq_list[index_freq])!= -1 or state_freq_list[index_freq] == "shut" )):
                            self.listbox_files.insert(tk.END, file)
                            #self.file_list_sort.append(file)

                    else:
                        if(file.endswith(state_format_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or state_freq_list[index_freq] == "shut" ):
                            self.listbox_files.insert(tk.END, file)
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
                # Sauvegarder l'image en format JPEG
                file_save_path = fd.asksaveasfilename(filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg")])
                self.figure.savefig(file_save_path)
        except:
            print("Erreur lors de la sauvegarde de l'image.")
            traceback.print_exc()

    def save_all(self):
        try:
            event = None
            if self.file_list_sort:
                folder_path = fd.askdirectory()
                for file in self.listbox_files.get(0, tk.END):
                    file_path = os.path.join(self.selected_directory, file)
                    self.update_canvas_image()

                    self.img = self.Rdata.rd_img(file_path)

                    self.img_modified = self.img[int(self.ysca1):int(self.ysca2),:]
                    self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, self.t0_lin_value - int(self.ysca1), self.t0_exp_value - int(self.ysca2), self.gain_const_value, self.gain_lin_value, self.gain_exp_value)

                    if(self.dewow_button_text.get() == "Dewow activé"):
                        self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

                    if(self.sub_mean_value != None):
                        self.img_modified = self.Rcontroller.sub_mean(self.img_modified, self.sub_mean_value)

                    if(self.inv_button_text.get() == "Inversement pairs activé"):
                        if(self.file_index % 2 != 0):
                            self.img_modified = np.fliplr(self.img_modified)

                    if(self.inv_solo_button_text.get() == "Inversement activé"):
                        self.img_modified = np.fliplr(self.img_modified)
                    
                    if(self.equalization_button_text.get() == "Égalisation activée"):
                        if self.img_modified.shape[1] < self.max_tr:
                        # Ajouter des colonnes supplémentaires
                            additional_cols = self.max_tr - self.img_modified.shape[1]
                            self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')

                    self.update_axes(event, self.epsilon)

                    # Sauvegarder l'image en format PNG
                    file_save_path = folder_path + "/" + file[:-4] + ".png"
                    self.figure.savefig(file_save_path)
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Erreur lors de la sauvegarde des images.")
            traceback.print_exc()

    ### Menu --> Modifier ###
    
    ### Sidebar ###
    def sidebar(self, parent: tk.Frame):
        """
    Méthode qui crée le widget sidebar.

    Args:
                parent (tk.Frame): frame principale du logiciel 
        """
        sidebar_frame = tk.Frame(parent, width=self.sidebar_width(), padx = str(self.pad_length()))
        sidebar_frame.pack(side="left", fill="both", padx = str(self.pad_length()), pady = str(self.pad_length()))

        # Premier bloc: Liste des fichiers
        file_frame = tk.Frame(sidebar_frame)
        file_frame.pack(fill="both")

        list_frame = tk.Frame(file_frame)
        list_frame.pack(fill="both")

        file_label = tk.Label(list_frame, text="Fichiers", font=("Arial", 16, "bold"))
        file_label.pack()

        file_scrollbar_x = tk.Scrollbar(list_frame, orient="horizontal")
        file_scrollbar_x.pack(side="bottom", fill="x")

        file_scrollbar_y = tk.Scrollbar(list_frame, orient="vertical")
        file_scrollbar_y.pack(side="right", fill="y")

        self.listbox_files = tk.Listbox(list_frame, xscrollcommand=file_scrollbar_x.set, yscrollcommand=file_scrollbar_y.set)
        self.listbox_files.pack(side="left", fill="both", expand=True)
        self.listbox_files.bind("<<ListboxSelect>>", self.select_file)

        file_scrollbar_x.config(command=self.listbox_files.xview)
        file_scrollbar_y.config(command=self.listbox_files.yview)

        # Bouton de filtrage et de désactivation
        self.filter_button_text = tk.StringVar(value="Filtrage désactivé")
        filter_button = tk.Button(file_frame, textvariable=self.filter_button_text, command=self.filter_list_file)
        filter_button.pack(fill="both")

        self.mult_button_text = tk.StringVar(value=".rd7")
        disable_mult_button = tk.Button(file_frame, textvariable=self.mult_button_text, font=("Arial", 8, "bold"), command=self.filter_mult)
        disable_mult_button.pack(fill="both")

        # Bouton d'inversement de la liste de fichiers
        self.inv_button_text = tk.StringVar(value="Inversement pairs désactivé")
        inv_button = tk.Button(file_frame, textvariable=self.inv_button_text, command=self.inv_file_list)
        inv_button.pack(fill="both")
        
        # Deuxième bloc: Affichage
        display_frame = tk.Frame(sidebar_frame, pady=str(self.pad_length()))
        display_frame.pack(fill="both")

        display_label = tk.Label(display_frame, text = "Affichage", font=("Arial", 16, "bold"))
        display_label.pack(fill = "both")

        abs_label = tk.Label(display_frame, text="Unité en abscisse")
        abs_label.pack(fill = "both")

        self.abs_unit = ttk.Combobox(display_frame, values=self.Xunit, state="readonly")
        self.abs_unit.set("Distance")
        self.abs_unit.pack(fill="both")
        
        self.abs_unit.bind("<<ComboboxSelected>>", lambda event: self.update_axes(event, self.epsilon))

        ord_label = tk.Label(display_frame, text="Unité en ordonnée")
        ord_label.pack(fill = "both")

        self.ord_unit = ttk.Combobox(display_frame, values=["Profondeur", "Temps", "Samples"], state="readonly")
        self.ord_unit.set("Profondeur")
        self.ord_unit.pack(fill="both")

        self.ord_unit.bind("<<ComboboxSelected>>", lambda event: self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value))

        epsilon_frame = tk.Frame(display_frame)
        epsilon_frame.pack(fill="both")

        epsilon_label = tk.Label(epsilon_frame, text="\u03B5:", font=("Arial", 12))
        epsilon_label.grid(row=0, column=0)

        epsilon_entry = tk.Entry(epsilon_frame)
        epsilon_entry.grid(row=0, column=2)

        def update_epsilon_value():
            try:
                self.epsilon = float(epsilon_entry.get())
                if(self.epsilon <= 0.):
                    self.epsilon = 6.
                    print("La permitivité ne peut être inférieure ou égale 0 !")
            except:
                self.epsilon = 6.
                print("Aucune valeur de epsilon a été définie")
            return self.epsilon

        epsilon_entry.bind("<FocusOut>", lambda event: self.update_axes(event, update_epsilon_value()))

        separator5 = ttk.Separator(file_frame, orient="horizontal")
        separator5.pack(fill = "x")

        # Troisième bloc: Outils
        tool_frame = tk.Frame(sidebar_frame)
        tool_frame.pack(side="left", fill="both", expand=True)

        tool_label = tk.Label(tool_frame, text="Outils", font=("Arial", 16, "bold"))
        tool_label.pack(fill="both")

        # Widget Notebook
        notebook = ttk.Notebook(tool_frame)
        notebook.pack(fill="both", expand=True)

        # Premier onglet: Gains/Filtres
        gain_frame_ntb = ttk.Frame(notebook, padding=self.pad_length())
        notebook.add(gain_frame_ntb, text="Gains/Infos")

        # Titre
        gain_frame = tk.Frame(gain_frame_ntb)
        gain_frame.pack(fill="both")

        gain_label = tk.Label(gain_frame, text="Gains", font=("Arial", 14, "bold"))
        gain_label.pack()

        # Première partie: Champs des différents gains
        gain_const_frame = tk.Frame(gain_frame)
        gain_const_frame.pack(fill="both")

        gain_const_label = tk.Label(gain_const_frame, text="Gain constant:", font=("Arial", 12))
        gain_const_label.grid(row=0, column=0)

        gain_const_entry = tk.Entry(gain_const_frame)
        gain_const_entry.grid(row=0, column=1)

        def update_gain_const_value():
            try:
                gain_const_value = float(gain_const_entry.get())
                if(gain_const_value >= 0.):
                    self.gain_const_value = gain_const_value
            except:
                self.gain_const_value = 1.  # Valeur par défaut en cas d'erreur de conversion
            return self.gain_const_value
        
        gain_const_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))
        
        # Séparateur
        separator = ttk.Separator(gain_frame, orient="horizontal")
        separator.pack(fill="x")

        gain_lin_frame = tk.Frame(gain_frame)
        gain_lin_frame.pack(fill="both")

        gain_lin_label = tk.Label(gain_lin_frame, text="Gain linéaire:", font=("Arial", 12))
        gain_lin_label.grid(row=0, column=0)

        gain_lin_entry = tk.Entry(gain_lin_frame, )
        gain_lin_entry.grid(row=0, column=1)

        self.t0_lin_label = tk.Label(gain_lin_frame, text="t0" + self.ord_unit.get() + ":", font=("Arial", 12))
        self.t0_lin_label.grid(row=1, column=0)

        self.t0_lin_entry = tk.Entry(gain_lin_frame)
        self.t0_lin_entry.grid(row=1, column=1)

        form_lin_label = tk.Label(gain_lin_frame, text="Formule: a(x - t0)", font=("Arial", 8), highlightthickness=0)
        form_lin_label.grid(row=2, column=0)

        def update_gain_lin_value():
            try:
                gain_lin_entry_value = gain_lin_entry.get()
                t0_lin_entry_value = self.t0_lin_entry.get()
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                yindex = self.Yunit.index(self.ord_unit.get())

                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                if(gain_lin_entry_value.isdigit() or gain_lin_entry_value.find(".") != -1):
                    if(t0_lin_entry_value.isdigit() or t0_lin_entry_value.find(".") != -1):
                        if(float(t0_lin_entry_value) / L_mult[yindex] >= self.ysca1 and float(t0_lin_entry_value) / L_mult[yindex] <= self.ysca2):
                            self.t0_lin_value = int(float(t0_lin_entry_value) / L_mult[yindex])
                            self.gain_lin_value = float(gain_lin_entry_value)
                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_lin_entry.delete(0, tk.END) 
                            # Insère le message d'erreur
                            self.t0_lin_entry.insert(tk.END, "Erreur t0") 

                            self.t0_lin_value = int(self.ysca1)
                            self.gain_lin_value = float(gain_lin_entry_value)

                    else:
                        self.t0_lin_value = int(self.ysca1)
                        self.gain_lin_value = float(gain_lin_entry_value)

                        
                else:
                    if(t0_lin_entry_value.isdigit() or t0_lin_entry_value.find(".") != -1):
                        if(float(t0_lin_entry_value) / L_mult[yindex] >= self.ysca1 and float(t0_lin_entry_value) / L_mult[yindex] <= self.ysca2):
                            self.t0_lin_value = int(float(t0_lin_entry_value) / L_mult[yindex])
                            self.gain_lin_value = 0.
                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_lin_entry.delete(0, tk.END) 
                            # Insère le message d'erreur
                            self.t0_lin_entry.insert(tk.END, "Erreur t0") 

                            self.t0_lin_value = int(self.ysca1)
                            self.gain_lin_value = 0.

                    else:
                        self.t0_lin_value = int(self.ysca1)
                        self.gain_lin_value = 0.

            except:
                traceback.print_exc()
            return self.gain_lin_value, self.t0_lin_value
        
        gain_lin_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))
        self.t0_lin_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))

        # Séparateur
        separator1 = ttk.Separator(gain_frame, orient="horizontal")
        separator1.pack(fill="x")

        gain_exp_frame = tk.Frame(gain_frame)
        gain_exp_frame.pack(fill="both")

        gain_exp_label = tk.Label(gain_exp_frame, text="Gain exponentiel:", font=("Arial", 12))
        gain_exp_label.grid(row=0, column=0)

        gain_exp_entry = tk.Entry(gain_exp_frame)
        gain_exp_entry.grid(row=0, column=1)

        self.t0_exp_label = tk.Label(gain_exp_frame, text="t0" + self.ord_unit.get() + ":", font=("Arial", 12))
        self.t0_exp_label.grid(row=1, column=0)

        self.t0_exp_entry = tk.Entry(gain_exp_frame)
        self.t0_exp_entry.grid(row=1, column=1)

        def update_gain_exp_value():
            try:
                gain_exp_entry_value = gain_exp_entry.get()
                t0_exp_entry_value = self.t0_exp_entry.get()
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                yindex = self.Yunit.index(self.ord_unit.get())

                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                if(gain_exp_entry_value.isdigit() or gain_exp_entry_value.find(".") != -1):
                    if(t0_exp_entry_value.isdigit() or t0_exp_entry_value.find(".") != -1):
                        if(float(t0_exp_entry_value) / L_mult[yindex] >= self.ysca1 and float(t0_exp_entry_value) / L_mult[yindex] <= self.ysca2):
                            self.t0_exp_value = int(float(t0_exp_entry_value) / L_mult[yindex])
                            self.gain_exp_value = float(gain_exp_entry_value)

                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_exp_entry.delete(0, tk.END) 
                            # Insère le message d'erreur
                            self.t0_exp_entry.insert(tk.END, "Erreur t0 ") 

                            self.t0_exp_value = int(self.ysca1)
                            self.gain_exp_value = float(gain_exp_entry_value)

                    else:
                        self.t0_exp_value = int(self.ysca1)
                        self.gain_exp_value = float(gain_exp_entry_value)
                        
                else:
                    if(t0_exp_entry_value.isdigit() or t0_exp_entry_value.find(".") != -1):
                        if(float(t0_exp_entry_value) >= self.ysca1 and float(t0_exp_entry_value) <= self.ysca2):
                            self.t0_exp_value = int(float(t0_exp_entry_value) / L_mult[yindex])
                            self.gain_exp_value = 0.

                        else:
                            # Efface le contenu actuel de la zone de texte
                            self.t0_exp_entry.delete(0, tk.END) 
                            # Insère le message d'erreur
                            self.t0_exp_entry.insert(tk.END, "Erreur t0") 

                            self.t0_exp_value = int(self.ysca1)
                            self.gain_exp_value = 0.

                    else:
                        self.t0_exp_value = int(self.ysca1)
                        self.gain_exp_value = 0.
            except ValueError:
                traceback.print_exc()
            return self.gain_exp_value, self.t0_exp_value

        gain_exp_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))
        self.t0_exp_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))
        
        form_lin_label = tk.Label(gain_exp_frame, text="Formule: e^(a(x - t0))-1", font=("Arial", 8), highlightthickness=0)
        form_lin_label.grid(row=2, column=0)
        # Séparateur
        separator2 = ttk.Separator(gain_frame, orient="horizontal")
        separator2.pack(fill="x")

        # Titre
        data_frame = tk.Frame(gain_frame)
        data_frame.pack(fill="both")

        data_label = tk.Label(data_frame, text="Données de l'image", font=("Arial", 14, "bold"))
        data_label.pack()

        self.data_xlabel = tk.Label(data_frame, text=self.abs_unit.get()+":"+str(), font=("Arial", 10), highlightthickness=0)
        self.data_xlabel.pack()

        self.data_ylabel = tk.Label(data_frame, text=self.ord_unit.get()+":"+str(), font=("Arial", 10), highlightthickness=0)
        self.data_ylabel.pack()

        self.data_ant_radar = tk.Label(data_frame, text="Antenne radar:", font=("Arial", 10), highlightthickness=0)
        self.data_ant_radar.pack()


        # Deuxième onglet: Filtre et Découpage
        filter_cut_frame_ntb = ttk.Frame(notebook, padding=self.pad_length())
        notebook.add(filter_cut_frame_ntb, text="Filtres/Découpage")

        filter_frame = tk.Frame(filter_cut_frame_ntb)
        filter_frame.pack(fill="both")

        filter_label = tk.Label(filter_frame, text="Filtres", font=("Artial",14, "bold"))
        filter_label.pack()
        
        # Deuxième partie: Champs des différents Filtres
        dewow_filter_frame = tk.Frame(filter_frame)
        dewow_filter_frame.pack(fill="both")

        self.dewow_button_text = tk.StringVar(value="Dewow désactivé")
        dewow_button = tk.Button(dewow_filter_frame, textvariable=self.dewow_button_text, font=("Arial", 8, "bold"), command=self.dewow_butt)
        dewow_button.pack(fill="both")

        sub_mean_frame = tk.Frame(filter_frame)
        sub_mean_frame.pack(fill="both")

        sub_mean_label = tk.Label(sub_mean_frame, text="Trace Moyenne:", font=("Arial", 10))
        sub_mean_label.grid(row=0, column=0)

        self.sub_mean_entry = tk.Entry(sub_mean_frame)
        self.sub_mean_entry.grid(row=0, column=1)

        def update_sub_mean():
            try:
                event = None
                if(self.sub_mean_entry.get().isdigit()):
                    n_tr = self.feature[0]
                    d_max = self.feature[2]
                    step_time_acq = self.feature[5]
                    xindex = self.Xunit.index(self.abs_unit.get())

                    L_mult = [d_max / n_tr, step_time_acq, 1]
                    if(int(float(self.sub_mean_entry.get()) / L_mult[xindex]) >= 0. and int(float(self.sub_mean_entry.get()) / L_mult[xindex]) <= n_tr):
                        self.sub_mean_value = int(float(self.sub_mean_entry.get()) / L_mult[xindex])
                    else:
                        self.sub_mean_value = None
                        self.sub_mean_entry.delete(0, tk.END)
                        self.sub_mean_entry.insert(tk.END, "Erreur")
                return self.sub_mean_value
            except:
                print("Erreur Trace moyenne:")
                traceback.print_exc()
                return None
        
        self.sub_mean_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))

        low_pass_frame = tk.Frame(filter_frame)
        low_pass_frame.pack(fill="both")

        low_pass_label = tk.Label(low_pass_frame, text="Passe bas:", font=("Arial", 12, "bold"))
        low_pass_label.pack(fill="both")

        under_low_pass_frame = tk.Frame(filter_frame)
        under_low_pass_frame.pack(fill="both")

        cutoff_label = tk.Label(under_low_pass_frame, text="Fr coupure:", font=("Arial", 10))
        cutoff_label.grid(row=0, column=0)

        cutoff_label = tk.Label(under_low_pass_frame, text="Fr coupure:", font=("Arial", 10))
        cutoff_label.grid(row=0, column=0)

        self.cutoff_entry = tk.Entry(under_low_pass_frame)
        self.cutoff_entry.grid(row=0, column=1)

        sampling_label = tk.Label(under_low_pass_frame, text="Fr échantillonage:", font=("Arial", 10))
        sampling_label.grid(row=1, column=0)

        self.sampling_entry = tk.Entry(under_low_pass_frame)
        self.sampling_entry.grid(row=1, column=1)

        def update_low_pass():
            try:
                event = None
                if((self.cutoff_entry.get().isdigit() or self.cutoff_entry.get().find(".") != -1) and (self.sampling_entry.get().isdigit() or self.sampling_entry.get().find(".") != -1)):
                        cutoff_value = float(self.cutoff_entry.get())
                        sampling_value = float(self.sampling_entry.get())
                        if(cutoff_value >= 0 and sampling_value >= 0):
                            self.cutoff_value = cutoff_value
                            self.sampling_value = sampling_value
                        else:
                            self.cutoff_entry.delete(0, tk.END)
                            self.cutoff_entry.insert(tk.END, "Erreur")

                            self.sampling_entry.delete(0, tk.END)
                            self.sampling_entry.insert(tk.END, "Erreur")
                else:
                    self.cutoff_value = None
                    self.sampling_value = None

                return self.cutoff_value, self.sampling_value
            except:
                print("Erreur Trace moyenne:")
                traceback.print_exc()
                return None
            
        self.cutoff_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))
        self.sampling_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))

        scaling_frame = tk.Frame(filter_cut_frame_ntb, pady=str(self.pad_length()))
        scaling_frame.pack(fill="both")

        scaling_label = tk.Label(scaling_frame, text = "Découpage", font=("Arial", 14, "bold"))
        scaling_label.pack(fill="both")

        yscale_frame = tk.Frame(scaling_frame)
        yscale_frame.pack(fill="both")

        self.yscale_label1 = tk.Label(yscale_frame, text = self.ord_unit.get()+" Début", font = ("Arial, 8"))
        self.yscale_label1.grid(row = 0, column = 0)
        self.yscale1 = tk.Entry(yscale_frame)
        self.yscale1.grid(row = 0, column = 1)

        self.yscale_label2 = tk.Label(yscale_frame, text = self.ord_unit.get()+" Fin", font = ("Arial, 8"))
        self.yscale_label2.grid(row = 1, column = 0)
        self.yscale2 = tk.Entry(yscale_frame)
        self.yscale2.grid(row = 1, column = 1)

        tools_frame = tk.Frame(filter_cut_frame_ntb)
        tools_frame.pack(fill="both")
        
        tools_label = tk.Label(tools_frame, text="Outils", font=("Arial", 14, "bold"))
        tools_label.pack()

        inv_solo_frame = tk.Frame(tools_frame)
        inv_solo_frame.pack(fill="both")

        self.inv_solo_button_text = tk.StringVar(value="Inversement désactivé")
        inv_solo_button = tk.Button(inv_solo_frame, textvariable=self.inv_solo_button_text, font=("Arial", 8, "bold"), command=self.inv_solo)
        inv_solo_button.pack(fill="both")

        equalization_frame = tk.Frame(tools_frame)
        equalization_frame.pack()

        self.equalization_button_text = tk.StringVar(value="Égalisation désactivée")
        equalization_button = tk.Button(inv_solo_frame, textvariable=self.equalization_button_text, font=("Arial", 8, "bold"), command=self.equalization)
        equalization_button.pack(fill="both")

        def update_yscale_value():
            try:
                n_samp = self.feature[1]
                t_max = self.feature[3]
                p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                yindex = self.Yunit.index(self.ord_unit.get())

                L_mult = [p_max / n_samp, t_max / n_samp, 1]
                L_max = [p_max, t_max, n_samp]
                if(self.yscale1.get() != ''):
                    ysca1 = float(self.yscale1.get())
                    if(ysca1 >= 0.):
                        self.ysca1 = ysca1 / L_mult[yindex]
                else:
                    self.ysca1 = 0.
                if(self.yscale2.get() != ''):
                    ysca2 = float(self.yscale2.get())
                    if(ysca2 <= L_max[yindex]):
                        self.ysca2 = ysca2 / L_mult[yindex]
                else:
                    self.ysca2 = L_max[yindex] / L_mult[yindex]
            except:
                print(f"Erreur yscale:")
                traceback.print_exc()
            return self.ysca1, self.ysca2
        
        self.yscale1.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))
        self.yscale2.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(), update_gain_lin_value()[0], update_gain_exp_value()[0], update_yscale_value()[0], update_yscale_value()[1], update_sub_mean(), update_low_pass()[0], update_low_pass()[1]))

        def update_sidebar():
            sidebar_frame.configure(width=self.sidebar_width())

        self.update_sidebar = update_sidebar 

        self.window.bind("<Configure>", lambda event: self.window.after(0, self.update_sidebar))

    def sidebar_width(self):
        """
    Méthode appelé par sidebar, elle permet de récupérer la longueur de la fenêtre pour prendre le poucentage souhaité.
        """
        window_width = self.window.winfo_width()
        sidebar_width = int(( 15 / 100) * window_width)
        return sidebar_width

    def select_file(self, event):
        """
    Méthode permettant de sélectionner un fichier dans la liste des fichiers.
        """
        try:
            selected_file = self.listbox_files.get(self.listbox_files.curselection())
            self.file_index = self.listbox_files.curselection()[0]  # Index du fichier sélectionné
            self.file_path = os.path.join(self.selected_directory, selected_file)

            self.Rcontroller = RadarController()
            self.feature = self.Rdata.get_feature(self.file_path)

            yindex = self.Yunit.index(self.ord_unit.get())
            n_samp = self.feature[1]
            t_max = self.feature[3]
            p_max = (t_max * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2
            L_max = [p_max, t_max, n_samp]
            L_mult = [p_max / n_samp, t_max / n_samp, 1]

            self.ysca1 = int(self.ysca1)
            if(self.yscale1.get() == ''):
                self.ysca2 = int(L_max[yindex] / L_mult[yindex])

            self.max_tr = self.max_list_files()
            self.update_img(event,self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print("Problème à régler (Utilisateurs ne vous souciez pas de cela)")
            traceback.print_exc()

    def max_list_files(self):
        """
    Méthode permettant de récupérer le nombre de traces maximal parmis une liste de fichiers.
        """
        files = self.listbox_files.get(0, tk.END)
        max = 0
        for file in files:
            file_path = os.path.join(self.selected_directory, file)
            n_tr = self.Rdata.get_feature(file_path)[0]
            if(max < n_tr):
                max = n_tr
        return max

    def filter_list_file(self, ):
        """
    Méthode permettant de filtrer la liste de fichiers en fonction du type de fréquence.
        """
        try:
            state_freq_list = ["shut", "high", "low"]
            name_freq_list = ["Filtrage désactivé", "Haute Fréquence", "Basse Fréquence"]
            index = name_freq_list.index(self.filter_button_text.get()) + 1
            if(index+1 <= len(name_freq_list)):
                self.filter_button_text.set(name_freq_list[index])
                self.freq_state = state_freq_list[index]
                self.update_file_list()
            else:
                index = 0
                self.filter_button_text.set(name_freq_list[index])
                self.freq_state = state_freq_list[index]
                self.update_file_list()
        except:
            print(f"Aucun dossier sélectionné, filtrage impossible:")
            traceback.print_exc()

    def filter_mult(self):
        """
    Méthode permettant de filtrer la liste de fichier en fonction du format souhaité.
        """
        try:
            index = self.list_ext.index(self.mult_button_text.get()) + 1
            if(index+1 <= len(self.list_ext)):
                self.mult_button_text.set(self.list_ext[index])
                self.update_file_list()
            else:
                index = 0
                self.mult_button_text.set(self.list_ext[index])
                self.update_file_list()
        except:
            print(f"Aucun dossier sélectionné, filtrage impossible:")
            traceback.print_exc()

    def inv_file_list(self):
        """
    Méthode inversant certains fichiers afin d'avoir une spacialisation correcte (voir contexte de la prise des données par radar).
        """
        try:
            event = None
            inv_status = ["Inversement pairs désactivé", "Inversement pairs activé"]
            index = inv_status.index(self.inv_button_text.get()) + 1
            if(index+1 <= len(inv_status)):
                self.inv_button_text.set(inv_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.inv_button_text.set(inv_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv:")
            traceback.print_exc()

    def dewow_butt(self):
        """
    Méthode permettant d'apliquer le filtre dewow à l'aide d'un bouton.
        """
        try:
            event = None
            dewow_status = ["Dewow désactivé", "Dewow activé"]
            index = dewow_status.index(self.dewow_button_text.get()) + 1
            if(index+1 <= len(dewow_status)):
                self.dewow_button_text.set(dewow_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.dewow_button_text.set(dewow_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Dewow:")
            traceback.print_exc()

    def inv_solo(self):
        """
    Méthode permettant d'inverser votre matrice. L'inversion consiste à inverser les colonnes.
        """
        try:
            event = None
            inv_status = ["Inversement désactivé", "Inversement activé"]
            index = inv_status.index(self.inv_solo_button_text.get()) + 1
            if(index+1 <= len(inv_status)):
                self.inv_solo_button_text.set(inv_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.inv_solo_button_text.set(inv_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Inv_solo:")
            traceback.print_exc()

    def equalization(self):
        """
    Méthode permettant de mettre toutes les images à la même taille en rajoutant des colonnes.
        """
        try:
            event = None
            eq_status = ["Égalisation désactivée", "Égalisation activée"]
            index = eq_status.index(self.equalization_button_text.get()) + 1
            if(index+1 <= len(eq_status)):
                self.equalization_button_text.set(eq_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
            else:
                index = 0
                self.equalization_button_text.set(eq_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value, self.ysca1, self.ysca2, self.sub_mean_value, self.cutoff_value, self.sampling_value)
        except:
            print(f"Erreur Égalisation:")
            traceback.print_exc()

    def radargram(self, parent):
        """
    Méthode qui crée le widget radargram.
        """
        radargram = tk.Frame(parent)
        radargram.pack(side="left", fill="both", expand=True, padx=str(self.pad_length()), pady=str(self.pad_length()))

        radar_label = tk.Label(radargram, text="Radargramme", font=("Arial", 20, "bold"))
        radar_label.pack()

        # Premier bloc: Matrice
        self.img_container = tk.Frame(radargram)
        self.figure = Figure(figsize=(12, 8))
        self.axes = self.figure.add_subplot(1,1,1)

        self.canvas_img = FigureCanvasTkAgg(self.figure, master=self.img_container)
        self.canvas_img.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Initialisation des axes x et y
            # Réglages des axes
            # Déplacer l'axe des abscisses vers le haut
        self.axes.xaxis.set_ticks_position('top')
        self.axes.xaxis.set_label_position('top')
        self.axes.yaxis.set_ticks_position('left')
        self.axes.yaxis.set_label_position('left')

        self.axes.set_axis_off()

        self.img_container.pack(side="left", fill="both", expand=True)
        
    def update_img(self, event, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float, yscale1: float, yscale2: float, sub: int, cutoff: float, sampling: float):
        """
    Méthode qui met à jour notre image avec les différentes applications possibles.
        """
        start = time.time()
        self.update_canvas_image()
        try:
            self.axes.set_axis_on()
            self.img = self.Rdata.rd_img(self.file_path)

            self.img_modified = self.img[int(yscale1):int(yscale2),:]
            self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, t0_lin - int(yscale1), t0_exp - int(yscale2), g, a_lin, a)

            if(self.dewow_button_text.get() == "Dewow activé"):
                self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)

            if(self.cutoff_entry.get() != '' and self.sampling_entry.get() != ''):
                self.img_modified = self.Rcontroller.low_pass(self.img_modified, cutoff, sampling)

            if(sub != None):
                self.img_modified = self.Rcontroller.sub_mean(self.img_modified, sub)

            if(self.inv_button_text.get() == "Inversement pairs activé"):
                if(self.file_index % 2 != 0):
                    self.img_modified = np.fliplr(self.img_modified)

            if(self.inv_solo_button_text.get() == "Inversement activé"):
                self.img_modified = np.fliplr(self.img_modified)
            
            if(self.equalization_button_text.get() == "Égalisation activée"):
                if self.img_modified.shape[1] < self.max_tr:
                # Ajouter des colonnes supplémentaires
                    additional_cols = self.max_tr - self.img_modified.shape[1]
                    self.img_modified = np.pad(self.img_modified, ((0, 0), (0, additional_cols)), mode='constant')

            self.update_axes(event, self.epsilon)

        except:
            print(f"Aucun fichier sélectionné, affichage de l'image impossible:")
            traceback.print_exc()
        end = time.time()
        print(f"Durée en seconde de la méthode update_img: {end-start}")

    def update_axes(self, event, epsilon: float):
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

            xindex = self.Xunit.index(self.abs_unit.get())
            yindex = self.Yunit.index(self.ord_unit.get())
            L_xmax = [d_max, step_time*n_tr, n_tr]
            L_xmult = [d_max / n_tr, step_time, 1]
            L_ymult = [p_max / n_samp, t_max / n_samp, 1]

            X = []
            Y = []

            if(self.equalization_button_text.get() == "Égalisation activée"):
                X = np.linspace(0.,self.max_tr * L_xmult[xindex],10)
                self.axes.set_xlabel(self.Xlabel[xindex])
                Y = np.linspace(self.ysca1 * L_ymult[yindex], self.ysca2 * L_ymult[yindex], 10)
                self.axes.set_ylabel(self.Ylabel[yindex])
                    
            else:
                X = np.linspace(0.,L_xmax[xindex],10)
                self.axes.set_xlabel(self.Xlabel[xindex])
                Y = np.linspace(self.ysca1 * L_ymult[yindex], self.ysca2 * L_ymult[yindex], 10)
                self.axes.set_ylabel(self.Ylabel[yindex])

            self.axes.imshow(self.img_modified, cmap="gray", interpolation="nearest", aspect="auto", extent = [X[0],X[-1],Y[-1], Y[0]])
            self.update_scale_labels(epsilon)
            self.canvas_img.draw()

            self.prec_abs = self.abs_unit.get()
            self.prec_ord = self.ord_unit.get()
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

            xindex = self.Xunit.index(self.abs_unit.get())
            yindex = self.Yunit.index(self.ord_unit.get())
            L_xmax = [d_max, step_time*n_tr, n_tr]
            L_ymax = [p_max, t_max, n_samp]

            # Mettre à jour les yscales
            if(self.yscale1.get() != '' and self.prec_ord != self.ord_unit.get()):
                yscale1 = ceil((self.ysca1 / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.get())])

                # Efface le contenu actuel de la zone de texte
                self.yscale1.delete(0, tk.END)

                self.yscale1.insert(tk.END, str(yscale1))

            if(self.yscale2.get() != '' and self.prec_ord != self.ord_unit.get()):
                yscale2 = ceil((self.ysca2 / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.get())])

                # Efface le contenu actuel de la zone de texte
                self.yscale2.delete(0, tk.END)

                self.yscale2.insert(tk.END, str(yscale2))            

            # Mettre à jour les t0
            if(self.t0_lin_entry.get() != '' and self.prec_ord != self.ord_unit.get()):
                t0_lin_value = ceil((self.t0_lin_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.get())])

                # Efface le contenu actuel de la zone de texte
                self.t0_lin_entry.delete(0, tk.END)

                self.t0_lin_entry.insert(tk.END, str(t0_lin_value))

            if(self.t0_exp_entry.get() != '' and self.prec_ord != self.ord_unit.get()):
                t0_exp_value = ceil((self.t0_exp_value / n_samp) * L_ymax[self.Yunit.index(self.ord_unit.get())])
                
                # Efface le contenu actuel de la zone de texte
                self.t0_exp_entry.delete(0, tk.END)

                self.t0_exp_entry.insert(tk.END, str(t0_exp_value))

            # Mettre à jour le texte du label
            self.yscale_label1.config(text=self.ord_unit.get() + " Début")
            self.yscale_label2.config(text=self.ord_unit.get() + " Fin")

            self.t0_lin_label.config(text="t0" + self.ord_unit.get() + ":")
            self.t0_exp_label.config(text="t0" + self.ord_unit.get() + ":")

            self.data_xlabel.config(text=self.abs_unit.get() + ": {:.2f} {}".format(L_xmax[xindex], xLabel[xindex]))
            self.data_ylabel.config(text=self.ord_unit.get() + ": {:.2f} {}".format(L_ymax[yindex], yLabel[yindex]))

            self.data_ant_radar.config(text="Antenne radar: "+antenna)
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

    ### Padding ###
    def pad_length(self):
        """
    Méthode appelé par sidebar, elle permet de récupérer la hauteur de la fenêtre pour prendre le poucentage souhaité afin d'avoir un padx dynamique.
        """
        window_height = self.window.winfo_height()
        sidebar_height = int((1 / 100)* window_height)
        return sidebar_height