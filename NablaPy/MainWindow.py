import tkinter as tk
import RadarController
from tkinter import filedialog as fd
import os

class MainWindow():
    """Cette classe représente la fenêtre principale."""
    def __init__(self, appname):
        """
        Constructeur de la classe MainWindow.

        Args:
                window (Object from tk.Tk) : Fenêtre principale
                title (string): Nom de l'application
                posX (int): Position selon l'axe x de notre application
                posY (int): Position selon l'axe y de notre application
                per_sidebar (int): Pourcentage de la longueur de la barre latérale
        """
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
        """
        En contruction:
        file_menu.add_command(label="Open", command=self.file_menu_command)
        file_menu.add_command(label="Exit", command=self.quit)"""

        # Création du sous-menu View
        view_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Fenêtre", menu=view_menu)


    def open_menu_command(self):
        selected_directory = fd.askdirectory()
        print("Dossier sélectionné :", selected_directory)
        self.update_file_list(selected_directory)

    def update_file_list(self, directory):
        file_list = os.listdir(directory)
        self.file_listbox.delete(0, tk.END)
        for file in file_list:
            self.file_listbox.insert(tk.END, file)

    def save(self):
        "En construction"
        return 0

    def export(self):
        "En construction"
        return 0

    def sidebar(self,parent):
        sidebar = tk.Frame(parent, width=self.sidebar_width(), bg="black")
        sidebar.pack(side="left", fill="both",padx=str(self.width_pad()),pady=str(self.width_pad()))

        # Premier bloc: Liste des fichiers
        file_frame = tk.Frame(sidebar)
        file_frame.pack(fill="both")

        file_label = tk.Label(file_frame, text="Fichier", font=("Arial", 12, "bold"))
        file_label.pack()

        file_scrollbar = tk.Scrollbar(file_frame)
        file_scrollbar.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(file_frame, yscrollcommand=file_scrollbar.set)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        file_scrollbar.config(command=self.file_listbox.yview)

        # Deuxième bloc: Outils
        second_block = tk.Frame(sidebar, bg="red")
        second_block.pack(side="left", fill="both", expand=True)

        def update_sidebar():
            sidebar.configure(width=self.sidebar_width())

        self.window.bind("<Configure>", lambda event: self.window.after(1, update_sidebar))


    def sidebar_width(self):
        """Méthode appelé par sidebar, elle permet de récupérer la longueur de la fenêtre pour prendre le poucentage souhaité."""
        window_width = self.window.winfo_width()
        #print("Largeur de la fenêtre :", window_width)
        sidebar_width = int(( 15 / 100) * window_width)
        return sidebar_width

    def radargram(self, parent):
        radargram = tk.Frame(parent, bg="pink")
        radargram.pack(side="left", fill="both", expand=True, padx=str(self.width_pad()), pady=str(self.height_pad()))

        radar_label = tk.Label(radargram, text="Radar", font=("Arial", 12, "bold"))
        radar_label.pack()

        # Conteneur
        frames_container = tk.Frame(radargram)
        frames_container.pack(fill="both", expand=True)

        # Premier bloc: Matrice
        mat_frame = tk.Frame(frames_container, bg="green")
        mat_frame.pack(side="left", fill="both", expand=True)

        # Deuxième bloc: Impulsion
        impulsion_frame = tk.Frame(frames_container, bg="blue")
        impulsion_frame.pack(side="left", fill="both", expand=True)
        """
        def update_radargram():
            

        self.window.bind("<Configure>", lambda event: self.window.after(1, update_radargram()))"""


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
