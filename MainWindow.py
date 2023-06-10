import tkinter as tk
import RadarController,RadarData
from tkinter import filedialog as fd
from PIL import ImageTk
import mimetypes as mt
import os

########### Ajouter les extensions de vos données ###########

List_of_extension = ['.rd3','.rd7']
for i in range(len(List_of_extension)):
    mt.add_type('application/octet-stream', List_of_extension[i])

#############################################################

class MainWindow():
    """Cette classe représente la fenêtre principale."""
    def __init__(self, appname: str, data: RadarData, controller: RadarController):
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
        self.selected_directory = fd.askdirectory()
        print("Dossier sélectionné :", self.selected_directory)
        self.update_file_list(self.selected_directory)

    def update_file_list(self, directory):
        file_list = os.listdir(directory)
        self.file_listbox.delete(0, tk.END)
        for file in file_list:
            file_path = os.path.join(directory, file)
            if mt.guess_type(file_path)[0] == 'application/octet-stream':
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
        self.file_listbox.bind("<<ListboxSelect>>", self.select_file)

        file_scrollbar.config(command=self.file_listbox.yview)

        # Deuxième bloc: Outils
        second_block = tk.Frame(sidebar, bg="red")
        second_block.pack(side="left", fill="both", expand=True)

        def update_sidebar():
            sidebar.configure(width=self.sidebar_width())

        self.update_sidebar = update_sidebar 

        self.window.bind("<Configure>", lambda event: self.window.after(1, self.update_blocks))

    def select_file(self, event):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            file_path = os.path.join(self.selected_directory, selected_file)
            print("Chemin du Fichier sélectionné :", file_path)
            # Vous pouvez afficher le chemin complet du fichier dans un Label ou tout autre widget de votre choix

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
    