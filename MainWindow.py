# ajout des axes sauvegarde # trace moyenne # couper image # différent type d'interpolation # dewow # temps abscisse
import tkinter as tk 
from RadarData import RadarData
from RadarData import cste_global
from RadarController import RadarController
from tkinter import filedialog as fd
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
from math import sqrt, ceil
import traceback
import time
# le problème est dans update_img, int32, float64, 64, object
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
        self.img = np.zeros(4)
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
        self.epsilon = 1. # cas dans le vide (Impossible)

        self.sidebar(self.window_frame)

            # Radargramme
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
            self.selected_directory = fd.askdirectory(initialdir="/home/cytech/Mesure/Dourdan")
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
    
    def save(self):
        """
        Méthode qui sauvegarde l'image modifiée (ou non) du fichier sélectionné sous le format jpeg.
        """
        if self.file_path == "":
            print("Aucune image n'a encore été définie")
        else:
            # Sauvegarder l'image en format JPEG
            file_save_path = fd.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")]) #initialdir="") # ajout
            self.figure.savefig(file_save_path)

    def save_all(self):
        """
    Méthode qui sauvegarde l'ensemble des images présent dans la listbox sous le format jpeg.
        """
        try:
            if(self.file_list_sort != []):
                folder_path = fd.askdirectory()
                for file in self.listbox_files.get(0, tk.END):
                    figure = Figure(figsize=(12, 8))
                    axes = figure.add_subplot(111)
                    axes.xaxis = self.axes.xaxis
                    axes.yaxis = self.axes.yaxis
                    path_file = os.path.join(self.selected_directory, file)
                    img = self.Rcontroller.apply_total_gain(self.Rdata.rd_mat(path_file), self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)
                    i = 1
                    while(file[-i] != "."):
                        i+=1
                        # Sauvegarder l'image en format JPEG
                    plt.imsave(folder_path + "/" + file[:-i] + ".jpg", img, cmap="Greys")
        except:
            print("test erreur")
    
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
        self.filter_button_text = tk.StringVar(value="Filtrage désactivé")
        filter_button = tk.Button(file_frame, textvariable=self.filter_button_text, command=self.filter_list_file)
        filter_button.pack(fill="both")

        self.mult_button_text = tk.StringVar(value=".rd7")
        disable_mult_button = tk.Button(file_frame, textvariable=self.mult_button_text, font=("Arial", 8, "bold"), command=self.filter_mult)
        disable_mult_button.pack(fill="both")
        
        # Deuxième bloc: Affichage
        display_frame = tk.Frame(sidebar_frame, pady=str(self.pad_length()))
        display_frame.pack(fill="both")

        display_label = tk.Label(display_frame, text = "Affichage", font=("Arial", 16, "bold"))
        display_label.pack(fill = "both")

        abs_label = tk.Label(display_frame, text="Unité en abscisse")
        abs_label.pack(fill = "both")

        self.abs_unit = ttk.Combobox(display_frame, values=["Distance", "Temps", "Traces"], state="readonly")
        self.abs_unit.set("Distance")
        self.abs_unit.pack(fill="both")
        
        self.abs_unit.bind("<<ComboboxSelected>>", lambda event: self.update_axes(event, self.epsilon))

        ord_label = tk.Label(display_frame, text="Unité en ordonnée")
        ord_label.pack(fill = "both")

        self.ord_unit = ttk.Combobox(display_frame, values=["Profondeur", "Temps", "Samples"], state="readonly")
        self.ord_unit.set("Profondeur")
        self.ord_unit.pack(fill="both")

        self.ord_unit.bind("<<ComboboxSelected>>", lambda event: self.update_axes_combo(event, self.epsilon))

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

        scaling_frame = tk.Frame(sidebar_frame, pady=str(self.pad_length()))
        scaling_frame.pack(fill="both")

        scaling_label = tk.Label(scaling_frame, text = "Découpage", font=("Arial", 16, "bold"))
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
        
        self.yscale1.bind("<FocusOut>", lambda event: self.update_axes(event, self.epsilon))
        self.yscale2.bind("<FocusOut>", lambda event: self.update_axes(event, self.epsilon))

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
            except:
                self.gain_const_value = 1.0  # Valeur par défaut en cas d'erreur de conversion
            return self.gain_const_value
        
        gain_const_entry.bind("<FocusOut>", lambda event: self.update_img(event, self.t0_lin_value, self.t0_exp_value, update_gain_const_value(), self.gain_lin_value, self.gain_exp_value))
        
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
            except:
                self.gain_lin_value = 0.0  # Valeur par défaut
                self.t0_lin_value = 0  # Valeur par défaut
            return self.gain_lin_value, self.t0_lin_value
        
        gain_lin_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], self.t0_exp_value, self.gain_const_value, update_gain_lin_value()[0], self.gain_exp_value))
        t0_lin_entry.bind("<FocusOut>", lambda event: self.update_img(event, update_gain_lin_value()[1], self.t0_exp_value, self.gain_const_value, update_gain_lin_value()[0], self.gain_exp_value))

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
                self.gain_exp_value = 0.  # Valeur par défaut
                self.t0_exp_value = 0  # Valeur par défaut
            return self.gain_exp_value, self.t0_exp_value

        gain_exp_entry.bind("<FocusOut>", lambda event: self.update_img(event, self.t0_lin_value, update_gain_exp_value()[1], self.gain_const_value, self.gain_lin_value, update_gain_exp_value()[0]))
        t0_exp_entry.bind("<FocusOut>", lambda event: self.update_img(event, self.t0_lin_value, update_gain_exp_value()[1], self.gain_const_value, self.gain_lin_value, update_gain_exp_value()[0]))
        
        form_lin_label = tk.Label(gain_exp_frame, text="Formule: e^(a(x - t0))", font=("Arial", 8), highlightthickness=0)
        form_lin_label.grid(row=2, column=0)
        # Séparateur
        separator2 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator2.pack(fill="x")

        # Titre
        pass_filter_frame = tk.Frame(gain_filter_tab)
        pass_filter_frame.pack(fill="both")

        pass_filter_frame = tk.Label(pass_filter_frame, text="Filtres", font=("Arial", 12, "bold"))
        pass_filter_frame.pack()

        # Deuxième partie: Champs des différents Filtres
        dewow_filter_frame = tk.Frame(gain_filter_tab)
        dewow_filter_frame.pack(fill="both")
        
        self.dewow_button_text = tk.StringVar(value="Dewow: Off")
        dewow_button = tk.Button(dewow_filter_frame, textvariable=self.dewow_button_text, font=("Arial", 8, "bold"), command=self.dewow_butt)
        dewow_button.pack(fill="both")

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
            file_path = os.path.join(self.selected_directory, selected_file)

            self.file_path = file_path
            self.Rcontroller = RadarController()
            self.update_img_selected(event,self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)
        except:
            """
            print(f"Aucun fichier a été sélectionné (select_file):")
            traceback.print_exc()
            """
            print("Problème à régler (Utilisateurs ne vous souciez pas de cela)")
    
    def filter_list_file(self, ):
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

    def dewow_butt(self):
        try:
            event = None
            dewow_status = ["Dewow: Off", "Dewow: On"]
            index = dewow_status.index(self.dewow_button_text.get()) + 1
            if(index+1 <= len(dewow_status)):
                self.dewow_button_text.set(dewow_status[index])
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)
            else:
                index = 0
                self.update_img(event, self.t0_lin_value, self.t0_exp_value, self.gain_const_value, self.gain_lin_value, self.gain_exp_value)
                self.dewow_button_text.set(dewow_status[index])
        except:
            print(f"Erreur:")
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
        self.axes.set_xlabel("a")
        self.axes.set_ylabel("b")

        self.canvas_img = FigureCanvasTkAgg(self.figure, master=self.img_container)
        self.canvas_img.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas_img.draw()

    def update_img_selected(self, event, t0_lin: int | float, t0_exp: int | float, g: float, a_lin: float, a: float):
        try:
            self.yscale1.delete('0', 'end')
            self.yscale2.delete('0', 'end')
            self.img = self.Rdata.rd_mat(self.file_path)
            self.img_modified = self.Rcontroller.apply_total_gain(self.img, t0_lin, t0_exp, g, a_lin, a)
            # Initialisation des axes x et y avec 15 graduations
                # Réglages des axes
                # Déplacer l'axe des abscisses vers le haut
            self.axes.xaxis.set_ticks_position('top')
            self.axes.xaxis.set_label_position('top')
            self.axes.yaxis.set_ticks_position('left')
            self.axes.yaxis.set_label_position('left')

            self.update_axes(event, self.epsilon)

            self.img_container.pack(side="left", fill="both", expand=True)

            if(self.dewow_button_text.get() == "Dewow: On"):
                self.dewow_button_text.set("Dewow: Off")

        except:
            print(f"Aucun fichier sélectionné, affichage de l'image impossible:")
            traceback.print_exc()

    def update_img(self, event, t0_lin: int | float, t0_exp: int | float, g: float, a_lin: float, a: float):
        try:
            if(self.yscale1.get() == '' or self.yscale2.get() == ''):
                self.img_modified = self.Rcontroller.apply_total_gain(self.img, t0_lin, t0_exp, g, a_lin, a)
                if(self.dewow_button_text.get() == "Dewow: On"):
                    self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)
            else:
                print("\nActuellement vous ne pouvez pas appliquer de gain à une image découpée !!!!\n")
                self.img_modified = self.Rcontroller.apply_total_gain(self.img_modified, t0_lin, t0_exp, g, a_lin, a)
                if(self.dewow_button_text.get() == "Dewow: On"):
                    self.img_modified = self.Rcontroller.dewow_filter(self.img_modified)


            self.update_axes(event, self.epsilon)

        except:
            print(f"Aucun fichier sélectionné, affichage de l'image impossible:")
            traceback.print_exc()
    
    def update_axes(self, event, epsilon):
        try:
            X = None
            Y = None
            if self.abs_unit.get() == "Distance":
                # Définition de l'axe Distance
                #    Distance de la mesure
                d_max = self.Rdata.get_feature(self.file_path)[2]
                # Génération des valeurs équidistantes pour les nouvelles étiquettes
                Distance = np.linspace(0., d_max, 20)

                # Modification des graduations
                X = Distance

                self.axes.set_xlabel("Distance en m")
            else:
                if self.abs_unit.get() == "Temps":
                    # Définition de l'axe Temps
                    #    Durée entre chaque mesure
                    step_time = self.Rdata.get_feature(self.file_path)[5]
                    if(step_time == 0.):
                        print("Acquisition des données en mode distance. Erreur d'affichage")

                    n_tr = self.Rdata.get_feature(self.file_path)[0]
                    # Génération des valeurs équidistantes pour les nouvelles étiquettes
                    Time_H = np.linspace(0., step_time*n_tr, 20)

                    # Modification des graduations
                    X = Time_H

                    self.axes.set_xlabel("Temps en s")
                else:
                    # Définition de l'axe Traces
                    #    Nombre de mesures
                    n_tr = self.Rdata.get_feature(self.file_path)[0]

                    # Génération des valeurs équidistantes pour les nouvelles étiquettes
                    Traces = np.linspace(0, n_tr, 20)
                    # Modification des graduations
                    X = Traces

                    self.axes.set_xlabel("Traces")

            if(self.yscale1.get() == '' or self.yscale2.get() == ''):
                if self.ord_unit.get() == "Samples":
                    # Définition de l'axe Samples
                    #    Nombre de d'échantillons
                    n_sam = self.Rdata.get_feature(self.file_path)[1]


                    Samples = np.linspace(0, n_sam, 20)
                    # Modification des graduations et étiquettes de l'axe des ordonnées
                    Y = Samples

                    self.axes.set_ylabel("Samples")

                else:
                    if self.ord_unit.get() == "Temps":
                        # Définition de l'axe Temps
                        t_max = self.Rdata.get_feature(self.file_path)[2] / 2

                        Time = np.linspace(0., t_max, 20)
                        # Modification des graduations et étiquettes de l'axe des ordonnées
                        Y = Time

                        self.axes.set_ylabel("Temps en ns")

                    else:
                        # Définition de l'axe Profondeur
                        #    Profondeur maximale
                        p_max = (self.Rdata.get_feature((self.file_path))[3] * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2


                        Depth = np.linspace(0., p_max, 20)

                        # Modification des graduations et étiquettes de l'axe des ordonnées
                        Y = Depth

                        self.axes.set_ylabel("Profondeur en m")
            else:
                yscale1 = float(self.yscale1.get())
                yscale2 = float(self.yscale2.get())
                Unit = ["Profondeur", "Temps", "Samples"]
                Ylabel = ["Profondeur en m", "Temps en ns", "Samples"]
                index = Unit.index(self.ord_unit.get())
                if(self.ord_unit.get() == "Samples"):
                    if(yscale1 >= 0. and yscale1 < yscale2 and yscale2 <= self.img.shape[0]): 
                            Modified = np.linspace(int(yscale1), int(yscale2), 20)
                            Y = Modified
                            self.axes.set_ylabel(Ylabel[index])
                            self.img_modified = self.img[int(yscale1):int(yscale2), :]
                    else:
                        if(yscale1 > yscale2):
                                print("Début > Fin")
                        else:
                                print("Vous avez dépassé les limites de votre images")
                else:
                    if(self.ord_unit.get() == "Profondeur"):
                        p_max = (self.Rdata.get_feature((self.file_path))[3] * 10.**(-9)) * (cste_global["c_lum"] / sqrt(epsilon)) / 2
                        if(yscale1 >= 0. and yscale1 < yscale2 and yscale2 <= p_max):
                            Modified = np.linspace(yscale1, yscale2, 20)
                            Y = Modified
                            self.axes.set_ylabel(Ylabel[index])
                            mult_fact = p_max / self.img.shape[0]
                            self.img_modified = self.img[int(yscale1 / mult_fact):int(yscale2 / mult_fact), :]
                        else:
                            if(yscale1 > yscale2):
                                print("Début > Fin")
                            else:
                                print("Vous avez dépassé les limites de votre images")
                    else:
                        if(self.ord_unit.get() == "Temps"):
                            t_max = self.Rdata.get_feature(self.file_path)[2] / 2
                            if(yscale1 >= 0. and yscale1 < yscale2 and yscale2 <= t_max):
                                Modified = np.linspace(yscale1, yscale2, 20)
                                Y = Modified
                                self.axes.set_ylabel(Ylabel[index])
                                mult_fact = t_max / self.img.shape[0]
                                self.img_modified = self.img[int(yscale1 / mult_fact):int(yscale2 / mult_fact), :]
                                self.axes.imshow(self.img_modified, cmap="Greys", interpolation="nearest", aspect='auto')
                            else:
                                if(yscale1 > yscale2):
                                    print("Début > Fin")
                                else:
                                    print("Vous avez dépassé les limites de votre images")
            
            self.axes.imshow(self.img_modified, cmap="Greys", interpolation="nearest", aspect="auto", extent = [X[0],X[-1],Y[-1], Y[0]])
            self.update_scale_labels()
            self.canvas_img.draw()

        except:
            print(f"Erreur mais shape_mod = {self.img_modified.shape}")
            print("\n\nUn des champs de votre découpage est vide")
            #traceback.print_exc()

    def update_axes_combo(self, event, epsilon):
        self.yscale1.delete('0', 'end')
        self.yscale2.delete('0', 'end')
        self.update_axes(event, epsilon)


    def update_scale_labels(self):
        try:
            # Mettre à jour le texte du label
            self.yscale_label1.config(text=self.ord_unit.get() + " Début")
            
            # Mettre à jour le texte du label
            self.yscale_label2.config(text=self.ord_unit.get() + " Fin")
        except:
            print("Test:")
            traceback.print_exc()

    ### Padding ###
    def pad_length(self):
        """
    Méthode appelé par sidebar, elle permet de récupérer la hauteur de la fenêtre pour prendre le poucentage souhaité afin d'avoir un padx dynamique.
        """
        window_height = self.window.winfo_height()
        sidebar_height = int((1 / 100)* window_height)
        return sidebar_height