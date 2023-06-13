import tkinter as tk
from RadarData import RadarData 
from RadarController import RadarController
from tkinter import filedialog as fd
from tkinter import ttk
from PIL import ImageTk
import mimetypes as mt
import os
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
        self.posX = (int(self.window.winfo_screenwidth()) // 2 ) - (1200 // 2) # positionnement x sur l'écran
        self.posY = (int(self.window.winfo_screenheight()) // 2 ) - (800 // 2) # positionnement y sur l'écran
        # Geométrie
        self.window.geometry("{}x{}+{}+{}".format(1200, 800,self.posX,self.posY))
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
        self.disable_state = "off"
        self.sidebar(self.window_frame)

        # Radargramme
        self.radargram(self.window_frame)



    def menu(self):
        """Méthode qui crée le menu de notre application"""
        menu_bar = tk.Menu(self.window)
        self.window.config(menu=menu_bar)

        # Création du sous-menu File
        file_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir un dossier", command=self.open_menu_command)
        file_menu.add_command(label="Sauvegarder", command=self.save)
        file_menu.add_command(label="Exporter au format...", command=self.export)
        file_menu.add_command(label="Quitter", command=self.window.quit)

        # Création du sous-menu Edit
        edit_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Modifier", menu=edit_menu)
        edit_menu.add_command(label="Ajouter une extension", command=self.add_ext)
        edit_menu.add_command(label="Supprimer une extension", command=self.del_ext)

        """
        En contruction:
        file_menu.add_command(label="Open", command=self.file_menu_command)
        file_menu.add_command(label="Exit", command=self.quit)"""

        # Création du sous-menu View
        view_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Fenêtre", menu=view_menu)

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
        self.filter_list_file()


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

        # Bouton de filtrage et de désactation
        self.filter_button_text = tk.StringVar(value="Haute Fréquence")
        filter_button = tk.Button(file_frame, textvariable=self.filter_button_text, command=self.filter_list_file)
        filter_button.pack(fill="both")

        self.disable_button_text = tk.StringVar(value="Désactiver le filtrage de fréquence")
        disable_button = tk.Button(file_frame, textvariable=self.disable_button_text, command=self.disable_filter)
        disable_button.pack(fill="both")

        # Deuxième bloc: Outils
        second_block = tk.Frame(sidebar)
        second_block.pack(side="left", fill="both", expand=True)

        # Widget Notebook
        notebook = ttk.Notebook(second_block)
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

        # Séparateur
        separator1 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator1.pack(fill="x")

        gain_lin_frame = tk.Frame(gain_filter_tab)
        gain_lin_frame.pack(fill="both")

        gain_lin_label = tk.Label(gain_lin_frame, text="Gain linéaire", font=("Arial", 12, "bold"))
        gain_lin_label.pack()

        gain_lin_entry = tk.Entry(gain_lin_frame)
        gain_lin_entry.pack()

        # Séparateur
        separator2 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator2.pack(fill="x")

        gain_exp_frame = tk.Frame(gain_filter_tab)
        gain_exp_frame.pack(fill="both")

        gain_exp_label = tk.Label(gain_exp_frame, text="Gain exponentiel", font=("Arial", 12, "bold"))
        gain_exp_label.pack()

        gain_exp_entry = tk.Entry(gain_exp_frame)
        gain_exp_entry.pack()

        # Séparateur
        separator3 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator3.pack(fill="x")

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
        separator1 = ttk.Separator(gain_filter_tab, orient="horizontal")
        separator1.pack(fill="x")

        # Deuxième onglet: En construction
        construction_tab = ttk.Frame(notebook)
        notebook.add(construction_tab, text="En construction")

        construction_label = tk.Label(construction_tab, text="Cette partie est en construction...", font=("Arial", 12, "bold"))
        construction_label.pack()


        def update_sidebar():
            sidebar.configure(width=self.sidebar_width())

        self.update_sidebar = update_sidebar 

        self.window.bind("<Configure>", lambda event: self.window.after(1, self.update_blocks))

    def filter_list_file(self):
        try:
            self.file_listbox.delete(0, tk.END)
            if self.filter_state == "high":
                self.filter_state = "low"
                self.filter_button_text.set("Basse Fréquence")
                for file in self.file_list:
                    if(file.find("_1") != -1):
                        file_path = os.path.join(self.selected_directory, file)
                        if mt.guess_type(file_path)[0] == 'application/octet-stream':
                            self.file_listbox.insert(tk.END, file)
            else:
                self.filter_state = "high"
                self.filter_button_text.set("Haute Fréquence")
                for file in self.file_list:
                    if(file.find("_2") != -1):
                        file_path = os.path.join(self.selected_directory, file)
                        if mt.guess_type(file_path)[0] == 'application/octet-stream':
                            self.file_listbox.insert(tk.END, file)
        except Exception as e:
            # Inutile mais faut bien écrire quelque chose
            del(e)

    def disable_filter(self):
        try:
            self.file_listbox.delete(0, tk.END)
            if(self.disable_state == "off"):
                self.disable_state = "on"
                self.disable_button_text.set("Désactiver le filtrage de fréquence")
                if(self.filter_button_text == "Haute Fréquence"):
                    for file in self.file_list:
                        if(file.find("_1") != -1):
                            file_path = os.path.join(self.selected_directory, file)
                            if mt.guess_type(file_path)[0] == 'application/octet-stream':
                                self.file_listbox.insert(tk.END, file)
                else:
                    for file in self.file_list:
                        if(file.find("_2") != -1):
                            file_path = os.path.join(self.selected_directory, file)
                            if mt.guess_type(file_path)[0] == 'application/octet-stream':
                                self.file_listbox.insert(tk.END, file)

            else:
                self.disable_state = "off"
                self.disable_button_text.set("Activer le filtrage de fréquence")
                for file in self.file_list:
                    file_path = os.path.join(self.selected_directory, file)
                    if mt.guess_type(file_path)[0] == 'application/octet-stream':
                        self.file_listbox.insert(tk.END, file)
        except Exception as e:
            # Inutile mais faut bien écrire quelque chose
            del(e)

    def select_file(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            file_path = os.path.join(self.selected_directory, selected_file)
            self.controller = RadarController(self.data, file_path)
            print("Chemin du Fichier sélectionné :", file_path)
    
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

        """# Conteneur
        frames_container = tk.Frame(radargram)
        frames_container.pack(fill="both", expand=True)"""

        # Premier bloc: Matrice
        mat_frame = tk.Frame(radargram, bg="green", height=self.radargram_blocks_width()[0])
        mat_frame.pack(side="top", fill="both", expand=True)
        """
        photo = tk.Image.PhotoImage(image)
        image_label = tk.Label(mat_frame, image=photo)
        image_label.pack()"""

        # Deuxième bloc: Tool
        impulsion_frame = tk.Frame(radargram, bg="blue", height=self.radargram_blocks_width()[1])
        impulsion_frame.pack(side="top", fill="both", expand=True)


        def update_radargram():
            mat_frame.configure(width=self.radargram_blocks_width()[0])
            impulsion_frame.configure(width=self.radargram_blocks_width()[1])
        
        self.update_radargram = update_radargram

        self.window.bind("<Configure>", lambda event: self.window.after(1, self.update_blocks))

    def radargram_blocks_width(self):
        """Méthode appelé par radargram, elle permet de récupérer la longueur souhaité pour les deux sous fenêtres."""
        window_height= self.window.winfo_height()
        #print("Largeur de la fenêtre :", window_width)
        radargram_height = int(( 85 / 100) * window_height)
        mat_height = int((80 / 100) * radargram_height)
        tool_height= int((20 / 100) * radargram_height)
        return mat_height, tool_height
    
    def update_blocks(self):
        self.update_sidebar()
        self.update_radargram()

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
    