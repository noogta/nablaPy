import tkinter as tk
from RadarData import RadarData 
from RadarData import cste_global
from RadarController import RadarController
from tkinter import filedialog as fd
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import mimetypes as mt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
from math import sqrt, ceil
import time
import traceback

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

        # Création d'une instance de la classe RadarData
        self.data = RadarData()

        # Création de notre fenêtre principale
        self.window = tk.Tk()
        self.window.title(appname)

        # Placement de la fenêtre au mileu de l'écran
        self.posX = (int(self.window.winfo_screenwidth()) // 2 ) - (1400 // 2) # positionnement x sur l'écran
        self.posY = (int(self.window.winfo_screenheight()) // 2 ) - (800 // 2) # positionnement y sur l'écran

        # Geométrie de la fenêtre
        self.window.geometry("{}x{}+{}+{}".format(1400, 800,self.posX,self.posY))
        self.window.update()

        # Affichage des différentes parties et création des variables
            # Menu
        self.img = None
        self.file_list_sort = list[str]
        self.menu()

            # Frame principale
        self.window_frame = tk.Frame(self.window)
        self.window_frame.pack(fill="both", expand=True)

            # Barre de contrôle
                # État initial du filtre des fichiers
        self.list_ext = ["Format", ".rd3", ".rd7", ".DZT"]
        self.freq_state = "high"

                # Définition des valeurs des gains
        self.gain_const_value = 1.
        self.gain_lin_value = 0.
        self.t0_lin_value = 0.
        self.gain_exp_value = 0.
        self.t0_exp_value = 0.
        self.epsilon = 1. # cas dans le vide

        self.sidebar(self.window_frame)

            # Radargramme
        self.file_path = ""
        self.radargram(self.window_frame)
        # Fin du constructeur Mainwindow

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
        edit_menu.add_command(label="Ajouter une extension", command=self.add_ext)
        edit_menu.add_command(label="Supprimer une extension", command=self.del_ext)

        """
        En contruction:
        file_menu.add_command(label="Open", command=self.file_menu_command)
        file_menu.add_command(label="Exit", command=self.quit)"""

        # Création du sous-menu View
        view_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Fenêtre", menu=view_menu)

    ### Menu --> Fichier ###
    def open_menu_command(self):
        try:
            self.selected_directory = fd.askdirectory()
            self.update_file_list()
        except:
            print(f"Erreur lors de la sélection du dossier:")
            traceback.print_exc()


    def update_file_list(self):
        """
    Méthode qui met à jour la liste des fichiers du logiciel.
        """
        # Création de la variable de type list str, self.file_list
        self.file_list = os.listdir(self.selected_directory)

        # Trie de la liste
        self.file_list.sort()

        # Suppresion --> Actualisation de la listbox
        self.listbox_files.delete(0, tk.END)

        # États/Formats pour le filtrage par fréquence
        state_freq_list = ["high", "low", "shut"]
        format_freq_list = ["_1","_2",""]
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
                    if((file.find(format_freq_list[index_freq] or state_freq_list[index_freq] == "shut" ) != -1)):
                        self.listbox_files.insert(tk.END, file)
                        #self.file_list_sort.append(file)

                else:
                    if(file.endswith(state_format_list[index_format])) and (file.find(format_freq_list[index_freq]) != -1 or state_freq_list[index_freq] == "shut" ):
                        self.listbox_files.insert(tk.END, file)
    
    def save(self):
        """
    Méthode qui sauvegarde l'image modifiée (ou non) du fichier sélectionné sous le format jpeg.
        """
        if(self.file_path == ""):
            print("Aucune image n'a encore été définie")
        else:
            # Sauvegarder l'image en format JPEG
            file_save_path = fd.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            plt.imsave(file_save_path, self.img, cmap="Greys")


    def save_all(self):
        """
    Méthode qui sauvegarde l'ensemble des images présent dans la listbox sous le format jpeg.
        """
        if(self.file_list_sort != []):
            folder_path = fd.askdirectory()
            for file in self.listbox_files.get(0, tk.END):
                path_file = os.path.join(self.selected_directory, file)
                img = self.data.rd_mat(path_file)
                img = self.controller.apply_total_gain(img, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)

                i = 1
                while(file[-i] != "."):
                    i+=1
                    # Sauvegarder l'image en format JPEG
                plt.imsave(folder_path + "/" + file[:-i] + ".jpg", img, cmap="Greys")

    ### Menu --> Modifier ###
    def add_ext(self):
        length = 600
        window_add = tk.Toplevel()
        window_add.title("Ajouter une extension")
        window_add.geometry("{}x{}+{}+{}".format(length, length, self.posX + (self.window.winfo_width()-length) // 2 ,self.posY+30))
    
    def del_ext(self):
        window_add = tk.Toplevel()
        window_add.title("Supprimer une extension")
        window_add.geometry("{}x{}+{}+{}".format(400, 400,self.posX + (self.window.winfo_width()-400) // 2 ,self.posY+30))
    
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
        self.filter_button_text = tk.StringVar(value="Haute Fréquence")
        filter_button = tk.Button(file_frame, textvariable=self.filter_button_text, command=self.filter_list_file)
        filter_button.pack(fill="both")

        self.mult_button_text = tk.StringVar(value="Format")
        disable_mult_button = tk.Button(file_frame, textvariable=self.mult_button_text, font=("Arial", 8, "bold"), command=self.filter_mult)
        disable_mult_button.pack(fill="both")
        
        # Deuxième bloc: Affichage
        display_frame = tk.Frame(sidebar_frame, pady=str(2 * self.pad_length()))
        display_frame.pack(fill="both")

        display_label = tk.Label(display_frame, text = "Affichage", font=("Arial", 16, "bold"))
        display_label.pack(fill = "both")

        abs_label = tk.Label(display_frame, text="Unité en abscisse")
        abs_label.pack(fill = "both")

        self.abs_unit = ttk.Combobox(display_frame, values=["Traces", "Distance"], state="readonly")
        self.abs_unit.set("Traces")
        self.abs_unit.pack(fill="both")
        
        self.abs_unit.bind("<<ComboboxSelected>>", lambda event: self.update_axes(event, self.epsilon))

        ord_label = tk.Label(display_frame, text="Unité en ordonnée")
        ord_label.pack(fill = "both")

        self.ord_unit = ttk.Combobox(display_frame, values=["Samples", "Temps","Profondeur"], state="readonly")
        self.ord_unit.set("Samples")
        self.ord_unit.pack(fill="both")

        self.ord_unit.bind("<<ComboboxSelected>>", lambda event: self.update_axes(event, self.epsilon))

        epsilon_frame = tk.Frame(display_frame)
        epsilon_frame.pack(fill="both")

        epsilon_label = tk.Label(epsilon_frame, text="\u03B5:", font=("Arial", 12))
        epsilon_label.grid(row=0, column=0)

        epsilon_entry = tk.Entry(epsilon_frame)
        epsilon_entry.grid(row=0, column=2)

        def update_epsilon_value():
            try:
                self.epsilon = float(epsilon_entry.get())
            except ValueError:
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
        gain_filter_tab = ttk.Frame(notebook, padding=self.pad_length())
        notebook.add(gain_filter_tab, text="Gains/Filtres")

        # Titre
        gain_frame = tk.Frame(gain_filter_tab)
        gain_frame.pack(fill="both")

        gain_label = tk.Label(gain_frame, text="Gains", font=("Arial", 14, "bold"))
        gain_label.pack()

        # Première partie: Champs des différents gains
        gain_const_frame = tk.Frame(gain_filter_tab)
        gain_const_frame.pack(fill="both")

        gain_const_label = tk.Label(gain_const_frame, text="Gain constant:", font=("Arial", 12))
        gain_const_label.grid(row=0, column=0)

        gain_const_entry = tk.Entry(gain_const_frame)
        gain_const_entry.grid(row=0, column=1)

        def update_gain_const_value():
            try:
                self.gain_const_value = float(gain_const_entry.get())
            except ValueError:
                self.gain_const_value = 1.0  # Valeur par défaut en cas d'erreur de conversion
            return self.gain_const_value

        gain_const_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        
        # Séparateur
        separator = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator.pack(fill="x")

        gain_lin_frame = tk.Frame(gain_filter_tab)
        gain_lin_frame.pack(fill="both")

        gain_lin_label = tk.Label(gain_lin_frame, text="Gain linéaire:", font=("Arial", 12))
        gain_lin_label.grid(row=0, column=0)

        gain_lin_entry = tk.Entry(gain_lin_frame, )
        gain_lin_entry.grid(row=0, column=1)

        t0_lin_label = tk.Label(gain_lin_frame, text="t0:", font=("Arial", 12))
        t0_lin_label.grid(row=1, column=0)

        t0_lin_entry = tk.Entry(gain_lin_frame)
        t0_lin_entry.grid(row=1, column=1)

        form_lin_label = tk.Label(gain_lin_frame, text="Formule: a(x - t0)", font=("Arial", 8), highlightthickness=0)
        form_lin_label.grid(row=2, column=0)


        def update_gain_lin_value():
            try:
                self.gain_lin_value = float(gain_lin_entry.get())
                t0_lin_entry_value = t0_lin_entry.get()
                if isinstance(self.gain_lin_value, float) and t0_lin_entry_value.isdigit():
                    self.t0_lin_value = int(t0_lin_entry_value)
                else:
                    self.t0_lin_value = 0
            except ValueError:
                self.gain_lin_value = 0.0  # Valeur par défaut
                self.t0_lin_value = 0  # Valeur par défaut
            return self.gain_lin_value, self.t0_lin_value

        gain_lin_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0], update_gain_exp_value()[0]))
        t0_lin_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))

        # Séparateur
        separator1 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator1.pack(fill="x")

        gain_exp_frame = tk.Frame(gain_filter_tab)
        gain_exp_frame.pack(fill="both")

        gain_exp_label = tk.Label(gain_exp_frame, text="Gain exponentiel:", font=("Arial", 12))
        gain_exp_label.grid(row=0, column=0)

        gain_exp_entry = tk.Entry(gain_exp_frame)
        gain_exp_entry.grid(row=0, column=1)

        t0_exp_label = tk.Label(gain_exp_frame, text="t0:", font=("Arial", 12))
        t0_exp_label.grid(row=1, column=0)

        t0_exp_entry = tk.Entry(gain_exp_frame)
        t0_exp_entry.grid(row=1, column=1)

        def update_gain_exp_value():
            try:
                self.gain_exp_value = float(gain_exp_entry.get())
                t0_exp_entry_value = t0_exp_entry.get()
                if isinstance(self.gain_exp_value, float) and t0_exp_entry_value.isdigit():
                    self.t0_exp_value = int(t0_exp_entry_value)
                else:
                    self.t0_exp_value = 0
            except ValueError:
                self.gain_exp_value = 0.0  # Valeur par défaut
                self.t0_exp_value = 0  # Valeur par défaut
            return self.gain_exp_value, self.t0_exp_value
        
        gain_exp_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        t0_exp_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        
        form_lin_label = tk.Label(gain_exp_frame, text="Formule: e^(a(x - t0))", font=("Arial", 8), highlightthickness=0)
        form_lin_label.grid(row=2, column=0)
        # Séparateur
        separator2 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator2.pack(fill="x")

        # Titre
        """
        pass_filter_frame = tk.Frame(gain_filter_tab)
        pass_filter_frame.pack(fill="both")

        pass_filter_frame = tk.Label(pass_filter_frame, text="Filtres", font=("Arial", 12, "bold"))
        pass_filter_frame.pack()

        # Deuxième partie: Champs des différents Filtres
        high_pass_filter_frame = tk.Frame(gain_filter_tab)
        high_pass_filter_frame.pack(fill="both")

        high_pass_filter_frame_label = tk.Label(high_pass_filter_frame, text="Filtre passe-haut", font=("Arial", 12, "bold"))
        high_pass_filter_frame_label.grid(row=0, column=0)

        high_pass_filter_entry = tk.Entry(high_pass_filter_frame)
        high_pass_filter_entry.grid(row=0, column=1)

        low_pass_filter_frame = tk.Frame(gain_filter_tab)
        low_pass_filter_frame.pack(fill="both")

        low_pass_filter_frame_label = tk.Label(low_pass_filter_frame, text="Filtre passe-haut", font=("Arial", 12, "bold"))
        low_pass_filter_frame_label.grid(row=0, column=0)

        low_pass_filter_entry = tk.Entry(low_pass_filter_frame)
        low_pass_filter_entry.grid(row=0, column=1)
        """

        # Deuxième onglet: En construction
        construction_tab = ttk.Frame(notebook)
        notebook.add(construction_tab, text="En construction")

        construction_label = tk.Label(construction_tab, text="Cette partie est en construction...", font=("Arial", 12, "bold"))
        construction_label.pack()


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
        try:
            selected_file = self.listbox_files.get(self.listbox_files.curselection())
            print(f"Voici:{selected_file}")
            file_path = os.path.join(self.selected_directory, selected_file)
            self.controller = RadarController(self.data)
            self.file_path = file_path
            self.update_img(event,0,0,1.0,0.0,0.0)
        except:
            """
            print(f"Aucun fichier a été sélectionné (select_file):")
            traceback.print_exc()
            """
            print("Problème à régler")
    
    def filter_list_file(self, ):
        try:
            state_freq_list = ["high", "low", "shut"]
            name_freq_list = ["Haute Fréquence", "Basse Fréquence", "Filtrage désactivé"]
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


    def radargram(self, parent):
        radargram = tk.Frame(parent)
        radargram.pack(side="left", fill="both", expand=True, padx=str(self.pad_length()), pady=str(self.pad_length()))

        radar_label = tk.Label(radargram, text="Radargramme", font=("Arial", 20, "bold"))
        radar_label.pack()

        # Premier bloc: Matrice
        self.img_container = tk.Frame(radargram)
        self.figure = Figure(figsize=(12, 8))
        self.axes = self.figure.add_subplot(111)
        
        self.canvas_img = FigureCanvasTkAgg(self.figure, master=self.img_container)
        self.canvas_img.draw()
        self.canvas_img.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_img(self, event, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float):
        try:
            img = self.data.rd_mat(self.file_path)
            self.img = self.controller.apply_total_gain(img, t0_lin, t0_exp, g, a_lin, a)
            
            # Réglages des axes
            # Déplacer l'axe des abscisses vers le haut
            self.axes.xaxis.set_ticks_position('top')
            self.axes.xaxis.set_label_position('top')
            self.axes.yaxis.set_ticks_position('left')
            self.axes.yaxis.set_label_position('left')

            n_tr = self.data.get_rad(self.file_path)[0]
            Traces = np.linspace(0, n_tr, 15)
            self.axes.set_xticks(Traces)
            self.axes.set_xticklabels([f"{int(ceil(tick))}" for tick in Traces])
            self.axes.set_xlabel("Trace")

            n_sam = self.data.get_rad(self.file_path)[1]
            Samples = np.linspace(0, n_sam, 15)
            self.axes.set_yticks(Samples)
            self.axes.set_yticklabels([f"{int(tick)}" for tick in Samples])
            self.axes.set_ylabel("Sample")
            self.axes.imshow(self.img, cmap="Greys", interpolation="nearest", aspect="auto")

            self.update_axes(event,self.epsilon)

            self.img_container.pack(side="left", fill="both", expand=True)

        except:
            print(f"Aucun fichier sélectionné, Affichage de l'image impossible:")
            traceback.print_exc()


    def update_axes(self, event, epsilon):
        try:
            if(self.file_path.endswith(".rd3") or self.file_path.endswith(".rd7")):
                if self.abs_unit.get() == "Distance":
                    # Définition de l'axe Distance
                    #    Distance de la mesure
                    d_max = self.data.get_rad(self.file_path)[2]            
                    old_ticks_x = self.axes.get_xticks()
                    num_ticks_x = len(old_ticks_x)

                    # Génération des valeurs équidistantes pour les nouvelles étiquettes
                    Distance = np.linspace(0., d_max, num_ticks_x)
                    new_labels_x = [f"{tick:.2f}" for tick in Distance]

                    # Modification des graduations et étiquettes de l'axe des abscisses
                    self.axes.set_xticks(old_ticks_x)
                    self.axes.set_xticklabels(new_labels_x)
                    self.axes.set_xlabel("m")
                    # Rétablissement des limites de l'axe des abscisses
                    #self.axes.set_xlim(xlim[0], xlim[1])

                else:
                    # Définition de l'axe Traces
                    #    Nombre de mesures
                    n_tr = self.data.get_rad(self.file_path)[0]

                    old_ticks_x = self.axes.get_xticks()
                    num_ticks_x = len(old_ticks_x)

                    # Génération des valeurs équidistantes pour les nouvelles étiquettes
                    Traces = np.linspace(0, n_tr, num_ticks_x)
                    new_labels_x = [f"{int(ceil(tick))}" for tick in Traces]
                    # Modification des graduations et étiquettes de l'axe des abscisses
                    self.axes.set_xticks(old_ticks_x)
                    self.axes.set_xticklabels(new_labels_x)
                    self.axes.set_xlabel("Trace")

                    # Définition des limites de l'axe des abscisses
                    #self.axes.set_xlim(0)
                        
                if self.ord_unit.get() == "Samples":
                    # Définition de l'axe Samples
                    #    Nombre de d'échantillons
                    n_sam = self.data.get_rad(self.file_path)[1]

                    old_ticks_y = self.axes.get_yticks()
                    num_ticks_y = len(old_ticks_y)

                    Samples = np.linspace(0, n_sam,num_ticks_y)
                    new_labels_y = [f"{int(tick)}" for tick in Samples]
                    # Modification des graduations et étiquettes de l'axe des abscisses
                    self.axes.set_yticks(old_ticks_y)
                    self.axes.set_yticklabels(new_labels_y)
                    self.axes.set_ylabel("Sample")

                    # Définition des limites de l'axe des ordonnées
                    #self.axes.set_ylim(0)

                else:
                    if self.ord_unit.get() == "Temps":
                        # Définition de l'axe Temps
                        t_max = self.data.get_rad(self.file_path)[4]

                        old_ticks_y = self.axes.get_yticks()
                        num_ticks_y = len(old_ticks_y)

                        Time = np.linspace(0., t_max, num_ticks_y)
                        new_labels_y = [f"{tick:.2f}" for tick in Time]
                        # Modification des graduations et étiquettes de l'axe des abscisses
                        self.axes.set_yticks(old_ticks_y)
                        self.axes.set_yticklabels(new_labels_y)
                        self.axes.set_ylabel("ns")

                        # Définition des limites de l'axe des ordonnées
                        #self.axes.set_ylim(0.)

                    else:
                        # Définition de l'axe Distance
                        #    Profondeur maximale
                        p_max = (self.data.get_rad((self.file_path))[4] * 10.**(-9)) * (cste_global["c_lum"] / sqrt(self.epsilon)) / 2

                        old_ticks_y = self.axes.get_yticks()
                        num_ticks_y = len(old_ticks_y)

                        Depth = np.linspace(0., p_max, num_ticks_y)
                        new_labels_y = [f"{tick:.2f}" for tick in Depth]
                        # Modification des graduations et étiquettes de l'axe des abscisses
                        self.axes.set_yticks(old_ticks_y)
                        self.axes.set_yticklabels(new_labels_y)
                        self.axes.set_ylabel("m")
            else:
                if(self.file_path.endswith(".DZT")):
                    print("DZT en cours")
        except:
            print(f"test erreur:")
            traceback.print_exc()

        self.canvas_img.draw()

    ### Padding ###
    def pad_length(self):
        """
    Méthode appelé par sidebar, elle permet de récupérer la hauteur de la fenêtre pour prendre le poucentage souhaité afin d'avoir un padx dynamique.
        """
        window_height = self.window.winfo_height()
        sidebar_height = int((1 / 100)* window_height)
        return sidebar_height
