import arcade
import os
import tkinter as tk
from tkinter import filedialog

from Logica.MappeLogica import MappeLogica
from schermate.GiocoScreen import GiocoScreen
from utils.RectangleBorder import RectangleBorder
from utils.RoundedButtons import RoundedButton
import shutil

class MappeScreen(arcade.View):

    def __init__(self, flag=True):
        super().__init__()
        self.mappa = MappeLogica(self.window, flag)

    def setup(self):
        self.camera = arcade.camera.Camera2D()

    def on_show_view(self):
        arcade.set_background_color((240, 255, 240))
        self.setup()
        self.mappa._carica_locali()
        self.mappa.create_buttons()

    def on_update(self, delta_time):
        pass

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)

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

        for i, button in enumerate(self.mappa.buttons):
            button.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from schermate.MenuScreen import MenuScreen
            self.window.show_view(MenuScreen(True))

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.mappa.buttons:
            button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.mappa.buttons:
                btn.on_click(x, y)