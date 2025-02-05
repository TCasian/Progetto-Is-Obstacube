import os
import tkinter as tk
from tkinter import filedialog
import shutil
from websockets.headers import parse_extension_item


class GestoreMappe:
    def __init__(self):
        self.mappe = self.carica_mappe()
        self.selezionata = None

    def carica_mappe(self):
        mappe = []
        dir = "./Media/mappe"
        files = os.listdir("./Media/mappe")
        files = [f for f in files if os.path.isfile(os.path.join(dir, f))]
        files = [f for f in files if f.endswith(f".tmx")]
        for file in files:
            mappe.append(file[:-4])
        return mappe

    def aggiungi_mappa(self):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Seleziona un file .tmx",
            filetypes=[("File TMX", "*.tmx")]
        )

        if file_path:
            dest_directory = "./Media/mappe"
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(dest_directory, file_name)
            shutil.copy(file_path, dest_path)
            self.mappe.append(file_name[:-4])

    def elimina_mappa(self):
        if self.selezionata is not None:
            mappa_da_eliminare = self.mappe[self.selezionata]
            percorso_mappa = f"./Media/mappe/{mappa_da_eliminare}.tmx"
            if os.path.exists(percorso_mappa):
                print("Non rimuovo !!")

            self.mappe.remove(mappa_da_eliminare)
            self.selezionata = None