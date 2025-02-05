import os
import tkinter as tk
from tkinter import filedialog
import shutil

import arcade

from schermate.GiocoScreen import GiocoScreen
from utils.RoundedButtons import RoundedButton


class MappeLogica:
    def __init__(self, window, flag):
        self.mappe = []
        self.selezionata = None
        self.buttons = []
        self.flag = flag
        self.window = window

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

    def _carica_locali(self):
        dir = "./Media/mappe"
        files = os.listdir("./Media/mappe")
        files = [f for f in files if os.path.isfile(os.path.join(dir, f))]
        files = [f for f in files if f.endswith(f".tmx")]
        for file in files:
            self.mappe.append(file[:-4])

    def create_buttons(self):
        mappe_width = self.window.width - 100
        mappe_height = self.window.height - 100
        button_width = mappe_width * 0.08
        button_height = mappe_width * 0.08
        spacing = 10
        start_x = (self.window.width / 2) - ((button_width + spacing) * (10 / 2 - 0.5))

        start_y = self.window.height - 100
        altezza_col = 0
        self.buttons = []

        j = 0
        for i, nome in enumerate(self.mappe):
            j += 1
            if i % 10 == 0:
                altezza_col += (mappe_width * 0.08) + spacing
                j = 0

            button = RoundedButton(
                text=nome,
                center_x=start_x + (button_width + spacing) * j,
                center_y=start_y - altezza_col,
                width=button_width,
                height=button_height,
                bg_color=(240, 255, 240),
                bg_hover=(217, 147, 8),
                text_color=arcade.color.BLACK,
                text_size=16,
                hover_text_color=arcade.color.WHITE,
                bold=True,
                callback=lambda i=i: self.select_map(i),
                bg_selected=arcade.color.GREEN,
            )
            self.buttons.append(button)

        self.buttons.append(RoundedButton(
            text="Gioca",
            center_x=self.window.width / 2 - 350,
            center_y=120,
            width=300,
            height=60,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=16,
            hover_text_color=arcade.color.WHITE,
            bold=True,
            callback=lambda: self._gioca_mappa(self.selezionata),
        ))
        if self.flag:
            self.buttons.append(RoundedButton(
                text="Aggiungi",
                center_x=self.window.width / 2,
                center_y=120,
                width=300,
                height=60,
                bg_color=(240, 255, 240),
                bg_hover=(217, 147, 8),
                text_color=arcade.color.BLACK,
                text_size=16,
                hover_text_color=arcade.color.WHITE,
                bold=True,
                callback=lambda: self._apri_file_dialog()
            ))

            self.buttons.append(RoundedButton(
                text="Elimina",
                center_x=self.window.width / 2 + 350,
                center_y=120,
                width=300,
                height=60,
                bg_color=(240, 255, 240),
                bg_hover=(217, 147, 8),
                text_color=arcade.color.BLACK,
                text_size=16,
                hover_text_color=arcade.color.WHITE,
                bold=True,
                callback=lambda: self._elimina_mappa()
            ))

    def _apri_file_dialog(self):
        # Crea una finestra di dialogo per selezionare un file
        root = tk.Tk()
        root.withdraw()  # Nasconde la finestra principale di tkinter

        # Apri la finestra di dialogo per selezionare un file con estensione .tsx
        file_path = filedialog.askopenfilename(
            title="Seleziona un file .tmx",
            filetypes=[("File TMX", "*.tmx")]
        )

        if file_path:
            print(f"File selezionato: {file_path}")
            dest_directory = "./Media/mappe"
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(dest_directory, file_name)
            shutil.copy(file_path, dest_path)
            self.mappe.append(file_name[:-4])
            self.create_buttons()

    def _elimina_mappa(self):
        if self.selezionata is not None:
            print(f"Elimino la mappa {self.selezionata} cioe {self.mappe[self.selezionata]}")
            self.mappe.remove(self.mappe[self.selezionata])
            self.create_buttons()

    def _gioca_mappa(self, mappa):
        self.window.show_view(GiocoScreen(self.mappe[self.selezionata]+".tmx"))

    def select_map(self, numero_mappa):
        self.selezionata = numero_mappa

        for button in self.buttons:
            button.selected = False
        # Seleziona il bottone cliccato
        self.buttons[numero_mappa].selected = True
        self.selezionata = numero_mappa