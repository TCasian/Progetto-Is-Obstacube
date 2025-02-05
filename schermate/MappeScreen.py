import arcade
import os
import tkinter as tk
from tkinter import filedialog
import shutil

from Logica.MappeLogica import GestoreMappe
from schermate.GiocoScreen import GiocoScreen
from utils.RectangleBorder import RectangleBorder
from utils.RoundedButtons import RoundedButton

class MappeScreen(arcade.View):
    def __init__(self, flag=True):
        super().__init__()
        self.flag = flag
        self.selezionata = None
        self.buttons = []
        self.gestore_mappe = GestoreMappe()

    def setup(self):
        self.camera = arcade.camera.Camera2D()

    def on_show_view(self):
        arcade.set_background_color((240, 255, 240))
        self.setup()
        self.create_buttons()

    def create_buttons(self):
        mappe_width = self.window.width - 100
        button_width = mappe_width * 0.08
        button_height = mappe_width * 0.08
        spacing = 10
        start_x = (self.window.width / 2) - ((button_width + spacing) * (10 / 2 - 0.5))
        start_y = self.window.height - 100
        altezza_col = 0
        self.buttons = []

        j = 0
        for i, nome in enumerate(self.gestore_mappe.mappe):
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
            callback=lambda: self._gioca_mappa(),
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
                callback=self.gestore_mappe.aggiungi_mappa
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
                callback=self._elimina_mappa
            ))

    def _apri_file_dialog(self):
        # da collegare fuori perche create_buttons
        self.create_buttons()

    def _elimina_mappa(self):
        self.gestore_mappe.elimina_mappa()
        self.create_buttons()

    def _gioca_mappa(self):
        if self.selezionata is not None:
            self.window.show_view(GiocoScreen(self.gestore_mappe.mappe[self.selezionata] + ".tmx"))

    def select_map(self, numero_mappa):
        self.selezionata = numero_mappa
        self.gestore_mappe.selezionata = numero_mappa
        for button in self.buttons:
            button.selected = False
        self.buttons[numero_mappa].selected = True

    def on_draw(self):
        self.clear()
        self.camera.use()

        mappe_width = self.window.width - 100
        mappe_height = self.window.height - 100

        RectangleBorder(
            center_x=self.window.width / 2,
            center_y=self.window.height / 2,
            width=mappe_width,
            height=mappe_height,
            bg_color=(217, 147, 8),
            border=True
        ).draw()

        arcade.draw_text(
            text="MAPPE",
            y=self.window.height - 130,
            x=self.window.width / 2,
            anchor_x='center',
            font_size=45,
            bold=True,
        )

        for button in self.buttons:
            button.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from schermate.MenuScreen import MenuScreen
            self.window.show_view(MenuScreen(True))

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons:
                btn.on_click(x, y)
