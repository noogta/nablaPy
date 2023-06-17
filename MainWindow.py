import tkinter as tk
from RadarData import RadarData 
from RadarController import RadarController
from tkinter import filedialog as fd
from tkinter import ttk
from PIL import Image, ImageTk
import mimetypes as mt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np
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
        self.data = RadarData()
        self.window = tk.Tk()
        self.window.title(appname)
        self.window
        # Placement de la fenêtre au mileu de l'écran
        self.posX = (int(self.window.winfo_screenwidth()) // 2 ) - (1300 // 2) # positionnement x sur l'écran
        self.posY = (int(self.window.winfo_screenheight()) // 2 ) - (900 // 2) # positionnement y sur l'écran
        # Geométrie
        self.window.geometry("{}x{}+{}+{}".format(1300, 900,self.posX,self.posY))
        self.window.update()
        # Affichage des différentes parties

        # Menu
        self.menu()
        # Frame principale
        self.window_frame = tk.Frame(self.window, bg="white smoke")
        self.window_frame.pack(fill="both", expand=True)
        # Barre de contrôle
        # État initial du filtre
        self.filter_state = "high"
        self.sidebar(self.window_frame)

        # Radargramme
        self.file_path = ""
        self.radargram(self.window_frame)



    def menu(self):
        """Méthode qui crée le menu de notre application"""
        menu_bar = tk.Menu(self.window)
        self.menu_bar = menu_bar
        self.window.config(menu=self.menu_bar)

        # Création du sous-menu File
        file_menu = tk.Menu(menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir un dossier", command=self.open_menu_command)
        file_menu.add_command(label="Sauvegarder", command=self.save)
        file_menu.add_command(label="Exporter au format...", command=self.export)
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

    ### Fichier ###
    def open_menu_command(self):
        self.selected_directory = fd.askdirectory()
        print("Dossier sélectionné :", self.selected_directory)
        self.update_file_list(self.selected_directory)

    ### Modifier ###
    def add_ext(self):
        length = 600
        window_add = tk.Toplevel()
        window_add.title("Ajouter une extension")
        window_add.geometry("{}x{}+{}+{}".format(length, length, self.posX + (self.window.winfo_width()-length) // 2 ,self.posY+30))
    
    def del_ext(self):
        window_add = tk.Toplevel()
        window_add.title("Supprimer une extension")
        window_add.geometry("{}x{}+{}+{}".format(400, 400,self.posX + (self.window.winfo_width()-400) // 2 ,self.posY+30))

    def update_file_list(self, directory: str):
        self.set_list_of_extension()
        self.file_list = os.listdir(directory)
        self.file_list.sort()
        self.file_listbox.delete(0, tk.END)
        for file in self.file_list:
            file_path = os.path.join(self.selected_directory, file)
            if mt.guess_type(file_path)[0] == 'application/octet-stream':
                self.file_listbox.insert(tk.END, file)
        #self.filter_list_file()


    def save(self):
        "En construction"
        return 0
    

    def export(self):
        "En construction"
        return 0

    def sidebar(self, parent):
        sidebar = tk.Frame(parent, width=self.sidebar_width(), bg="black")
        sidebar.pack(side="left", fill="both", padx=str(self.width_pad()), pady=str(self.width_pad()))

        # Premier bloc: Liste des fichiers
        file_frame = tk.Frame(sidebar)
        file_frame.pack(fill="both")

        list_frame = tk.Frame(file_frame)
        list_frame.pack(fill="both")

        file_label = tk.Label(list_frame, text="Fichier", font=("Arial", 12, "bold"))
        file_label.pack()

        file_scrollbar_x = tk.Scrollbar(list_frame, orient="horizontal")
        file_scrollbar_x.pack(side="bottom", fill="x")

        file_scrollbar_y = tk.Scrollbar(list_frame, orient="vertical")
        file_scrollbar_y.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(list_frame, xscrollcommand=file_scrollbar_x.set, yscrollcommand=file_scrollbar_y.set)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.select_file)

        file_scrollbar_x.config(command=self.file_listbox.xview)
        file_scrollbar_y.config(command=self.file_listbox.yview)

        # Bouton de filtrage et de désactivation
        self.filter_button_text = tk.StringVar(value="Haute Fréquence")
        filter_button = tk.Button(file_frame, textvariable=self.filter_button_text, command=self.filter_list_file)
        filter_button.pack(fill="both")

        self.mult_button_text = tk.StringVar(value="Format")
        disable_mult_button = tk.Button(file_frame, textvariable=self.mult_button_text, font=("Arial", 8, "bold"), command=self.filter_mult)
        disable_mult_button.pack(fill="both")
        
        # Deuxième bloc: Affichage

        # Troisième bloc: Outils
        third_block = tk.Frame(sidebar)
        third_block.pack(side="left", fill="both", expand=True)

        # Widget Notebook
        notebook = ttk.Notebook(third_block)
        notebook.pack(fill="both", expand=True)

        # Premier onglet: Gains/Filtres
        gain_filter_tab = ttk.Frame(notebook)
        notebook.add(gain_filter_tab, text="Gains/Filtres")

        # Titre
        gain_frame = tk.Frame(gain_filter_tab)
        gain_frame.pack(fill="both")

        gain_label = tk.Label(gain_frame, text="Gain", font=("Arial", 12, "bold"))
        gain_label.pack()

        # Première partie: Champs des différents gains
        gain_const_frame = tk.Frame(gain_filter_tab)
        gain_const_frame.pack(fill="both")

        gain_const_label = tk.Label(gain_const_frame, text="Gain constant", font=("Arial", 12, "bold"))
        gain_const_label.pack()

        gain_const_entry = tk.Entry(gain_const_frame)
        gain_const_entry.pack()

        def update_gain_const_value():
            try:
                gain_const_value = float(gain_const_entry.get())
            except ValueError:
                gain_const_value = 1.0  # Valeur par défaut en cas d'erreur de conversion
                print("la valeur est bien 1.0")
            return gain_const_value

        gain_const_entry.bind("<Return>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        
        # Séparateur
        separator = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator.pack(fill="x")

        gain_lin_frame = tk.Frame(gain_filter_tab)
        gain_lin_frame.pack(fill="both")

        gain_lin_label = tk.Label(gain_lin_frame, text="Gain linéaire", font=("Arial", 12, "bold"))
        gain_lin_label.pack()

        gain_lin_entry = tk.Entry(gain_lin_frame, )
        gain_lin_entry.pack()

        t0_lin_label = tk.Label(gain_lin_frame, text="t0", font=("Arial", 12, "bold"))
        t0_lin_label.pack()

        t0_lin_entry = tk.Entry(gain_lin_frame)
        t0_lin_entry.pack()

        def update_gain_lin_value():
            try:
                gain_lin_value = float(gain_lin_entry.get())
                t0_lin_entry_value = t0_lin_entry.get()
                if isinstance(gain_lin_value, float) and t0_lin_entry_value.isdigit():
                    t0_lin_value = int(t0_lin_entry_value)
                else:
                    t0_lin_value = 0
            except ValueError:
                gain_lin_value = 0.0  # Valeur par défaut
                t0_lin_value = 0  # Valeur par défaut
            return gain_lin_value, t0_lin_value

        gain_lin_entry.bind("<Return>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        t0_lin_entry.bind("<Return>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))

        # Séparateur
        separator1 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator1.pack(fill="x")

        gain_exp_frame = tk.Frame(gain_filter_tab)
        gain_exp_frame.pack(fill="both")

        gain_exp_label = tk.Label(gain_exp_frame, text="Gain exponentiel", font=("Arial", 12, "bold"))
        gain_exp_label.pack()

        gain_exp_entry = tk.Entry(gain_exp_frame)
        gain_exp_entry.pack()

        t0_exp_label = tk.Label(gain_exp_frame, text="t0", font=("Arial", 12, "bold"))
        t0_exp_label.pack()

        t0_exp_entry = tk.Entry(gain_exp_frame)
        t0_exp_entry.pack()

        def update_gain_exp_value():
            try:
                gain_exp_value = float(gain_exp_entry.get())
                t0_exp_entry_value = t0_exp_entry.get()
                if isinstance(gain_exp_value, float) and t0_exp_entry_value.isdigit():
                    t0_exp_value = int(t0_exp_entry_value)
                else:
                    t0_exp_value = 0
            except ValueError:
                gain_exp_value = 0.0  # Valeur par défaut
                t0_exp_value = 0  # Valeur par défaut
            return gain_exp_value, t0_exp_value
        
        gain_exp_entry.bind("<Return>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        t0_exp_entry.bind("<Return>", lambda event: self.update_img(event, update_gain_lin_value()[1], update_gain_exp_value()[1], update_gain_const_value(),update_gain_lin_value()[0],update_gain_exp_value()[0]))
        
        # Séparateur
        separator2 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator2.pack(fill="x")

        # Titre
        pass_filter_frame = tk.Frame(gain_filter_tab)
        pass_filter_frame.pack(fill="both")

        pass_filter_frame = tk.Label(pass_filter_frame, text="Filtre", font=("Arial", 12, "bold"))
        pass_filter_frame.pack()

        # Deuxième partie: Champs des différents Filtres

        high_pass_filter_frame = tk.Frame(gain_filter_tab)
        high_pass_filter_frame.pack(fill="both")

        high_pass_filter_frame_label = tk.Label(high_pass_filter_frame, text="Filtre passe-haut", font=("Arial", 12, "bold"))
        high_pass_filter_frame_label.pack()

        high_pass_filter_entry = tk.Entry(high_pass_filter_frame)
        high_pass_filter_entry.pack()

        low_pass_filter_frame = tk.Frame(gain_filter_tab)
        low_pass_filter_frame.pack(fill="both")

        low_pass_filter_frame_label = tk.Label(low_pass_filter_frame, text="Filtre passe-haut", font=("Arial", 12, "bold"))
        low_pass_filter_frame_label.pack()

        low_pass_filter_entry = tk.Entry(low_pass_filter_frame)
        low_pass_filter_entry.pack()

        # Séparateur
        separator3 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator3.pack(fill="x")

        # Deuxième onglet: En construction
        construction_tab = ttk.Frame(notebook)
        notebook.add(construction_tab, text="En construction")

        construction_label = tk.Label(construction_tab, text="Cette partie est en construction...", font=("Arial", 12, "bold"))
        construction_label.pack()


        def update_sidebar():
            sidebar.configure(width=self.sidebar_width())

        self.update_sidebar = update_sidebar 

        self.window.bind("<Configure>", lambda event: self.window.after(0, self.update_blocks))

    def filter_list_file(self, ):
        try:
            self.file_listbox.delete(0, tk.END)
            if self.filter_state == "high":
                self.filter_state = "low"
                self.filter_button_text.set("Basse Fréquence")
                for file in self.file_list:
                    if(file.find("_2") != -1):
                        file_path = os.path.join(self.selected_directory, file)
                        if mt.guess_type(file_path)[0] == 'application/octet-stream':
                            self.file_listbox.insert(tk.END, file)
            else:
                if(self.filter_state == "low"):
                    self.filter_state = "shut"
                    self.filter_button_text.set("Filtrage désactiver")
                    for file in self.file_list:
                        file_path = os.path.join(self.selected_directory, file)
                        if mt.guess_type(file_path)[0] == 'application/octet-stream':
                                self.file_listbox.insert(tk.END, file)
                else:
                    self.filter_state = "high"
                    self.filter_button_text.set("Haute Fréquence")
                    for file in self.file_list:
                        if(file.find("_1") != -1):
                            file_path = os.path.join(self.selected_directory, file)
                            if mt.guess_type(file_path)[0] == 'application/octet-stream':
                                self.file_listbox.insert(tk.END, file)
        except Exception as e:
            # Inutile mais faut bien écrire quelque chose
            del(e)

    def filter_mult(self):
        try:
            return 0
        except Exception as e:
            del(e)

    def mult_file_list(self):
        try:
            # Liste des extensions
            list_ext = []

            #Vérification de la présence de plusieurs formats
            for file in self.file_list:
                i = 1
                while(file[-i] != "."):
                    i+=1
                ext = file[len(file)-i:]
                if(ext not in list_ext):
                    list_ext.append(ext)
            return list_ext
        except Exception as e:
            del(e)

    def select_file(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            file_path = os.path.join(self.selected_directory, selected_file)
            self.controller = RadarController(self.data)
            print("Chemin du Fichier sélectionné :", file_path)
            self.file_path = file_path
        self.update_img(event,0,0,1.0,0.0,0.0)
    
    def sidebar_width(self):
        """Méthode appelé par sidebar, elle permet de récupérer la longueur de la fenêtre pour prendre le poucentage souhaité."""
        window_width = self.window.winfo_width()
        #print("Largeur de la fenêtre :", window_width)
        sidebar_width = int(( 15 / 100) * window_width)
        return sidebar_width

    def radargram(self, parent):
        radargram = tk.Frame(parent, bg="pink")
        radargram.pack(side="left", fill="both", expand=True, padx=str(self.width_pad()), pady=str(self.height_pad()))

        radar_label = tk.Label(radargram, text="Radargramme", font=("Arial", 12, "bold"))
        radar_label.pack()

        # Premier bloc: Matrice
        self.img_container = tk.Frame(radargram, bg="green")
        self.figure = Figure(figsize=(6, 4))
        self.axes = self.figure.add_subplot()
        
        self.canvas_img = FigureCanvasTkAgg(self.figure, master=self.img_container)
        self.canvas_img.get_tk_widget().pack(side="top", fill="both", expand=True)
        # Création de l'étiquette pour afficher les valeurs
        """values_label = tk.Label(self.canvas_img, textvariable=f"x:0.00 , y: 0.00")
        values_label.pack(side=tk.TOP, anchor=tk.NE)"""

        self.window.bind("<Configure>", lambda event: self.window.after(0, self.update_blocks))

    def update_img(self, event, t0_lin: int, t0_exp: int, g: float, a_lin: float, a: float):
        try:
            path_file = self.file_path
            img = self.data.rd_mat(path_file)
            img = self.controller.apply_total_gain(img, t0_lin, t0_exp, g, a_lin, a)

            # Afficher la nouvelle image sur le canvas
            self.axes.imshow(img, cmap="Greys", interpolation="nearest", aspect = "auto")
            self.canvas_img.draw()

            # Mettre à jour l'étiquette pour afficher les valeurs
            #values_label = tk.Label(self.canvas_img, textvariable=f"x:0.00 , y: 0.00")
            #values_label.pack(side=tk.TOP, anchor=tk.NE)
            self.img_container.pack(side="top", fill="both", expand = True)


        except Exception as e:
            print(e)
    
    def update_blocks(self):
        self.update_sidebar()

    def width_pad(self):
        """Méthode appelé par sidebar, elle permet de récupérer la hauteur de la fenêtre pour prendre le poucentage souhaité afin d'avoir un padx dynamique."""
        window_height = self.window.winfo_height()
        #print("Hauteur de la fenêtre :", window_height)
        sidebar_height = int((1 / 100)* window_height)
        return sidebar_height
    
    def height_pad(self):
        """Méthode appelé par sidebar, elle permet de récupérer la hauteur de la fenêtre pour prendre le poucentage souhaité afin d'avoir un pady dynamique."""
        window_height = self.window.winfo_height()
        #print("Hauteur de la fenêtre :", window_height)
        sidebar_height = int((1 / 100)* window_height)
        return sidebar_height
    
    def set_list_of_extension(self):
        List_of_extension = self.data.get_list_extension()
        for i in range(len(List_of_extension)):
            mt.add_type('application/octet-stream', List_of_extension[i])
    
    #filtre trace moyenne