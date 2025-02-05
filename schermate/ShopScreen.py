import os
import time

import arcade
import xml.etree.ElementTree as ET

from Logica.ImpostazioniLogica import ImpostazioniLogica
from Logica.ShopLogica import ShopLogica
from Persistenza import PlayerJSON, SkinJSON
from utils.RectangleBorder import RectangleBorder
from utils.RoundedButtons import RoundedButton


class ShopScreen(arcade.View):

    def __init__(self):
        super().__init__()
        self.shop = ShopLogica(self.window)

    def setup(self):
        self.camera = arcade.camera.Camera2D()

    def on_show_view(self):
        arcade.set_background_color((240, 255, 240))
        self.setup()
        self.shop._carica_locali()
        self.shop.create_buttons()

    def on_update(self, delta_time):
        self.shop.update_animation(delta_time)

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        skin_width = self.window.width - 100
        skin_height = self.window.height - 70

        RectangleBorder(
            center_x=self.window.width / 2,
            center_y=self.window.height / 2,
            width=skin_width,
            height=skin_height,
            bg_color=(217, 147, 8),
            border=True
        ).draw()

        arcade.draw_text(
            text="SKIN",
            y=self.window.height - 100,
            x=self.window.width / 2,
            anchor_x='center',
            font_size=45,
            bold=True,
        )
        arcade.draw_text(
            text=self.shop.player["monete"],
            y=self.window.height - 100,
            x=self.window.width - 120,
            anchor_x='right',
            font_size=45,
            bold=True,
        )
        moneta_sprite = arcade.Sprite("Media/img/coin.png", scale=1.2)
        moneta_sprite.center_x = self.window.width - 80
        moneta_sprite.center_y = self.window.height- 80
        arcade.draw_texture_rect(moneta_sprite.texture, moneta_sprite.rect)

        self.draw_all_skins()
        for button in self.shop.buttons:
            button.draw()
        if self.shop.insufficienti:
            RectangleBorder(
                center_x=self.window.width / 2,
                center_y=self.window.height / 2,
                width=650,
                height=100,
                bg_color=(217, 147, 8),
                border=True
            ).draw()
            arcade.draw_text(
                text="Monete insufficienti",
                y=self.window.height/ 2,
                x=self.window.width / 2,
                anchor_x='center',
                anchor_y='center',
                font_size=45,
                bold=True,
        )


        # Stampa il nome delle skin sotto lo sprite
        for i, skin in enumerate(self.shop.skin_list):
            if i >= len(self.shop.sprites):  # Se non ci sono abbastanza sprite, interrompi
                #print(f"Attenzione: mancano sprite per {skin['nome']}")
                continue
            x_pos = self.shop.sprites[i].center_x
            y_pos = self.shop.sprites[i].center_y - 40
            arcade.draw_text(
                skin["nome"], x_pos, y_pos, arcade.color.BLACK, 14, anchor_x="center"
            )

            # Se la skin non è acquistata, mostra il costo sotto il nome
            if not skin["acquistata"]:
                arcade.draw_text(
                    f"{skin['costo']}G", x_pos, y_pos - 20, arcade.color.RED, 12, anchor_x="center"
                )

    def draw_all_skins(self):
        """
        Disegna tutte le skin caricate a schermo.
        In questo esempio, le skin vengono disposte in orizzontale, ognuna a una distanza fissa.
        """
        margin = 20  # spazio tra le skin
        # Posizione di partenza
        start_x = 100
        start_y = 100

        current_x = start_x

        for skin_name, skin_data in self.shop.frames_dict.items():
            # Seleziona il primo frame della skin
            frame_texture = skin_data["frames"][skin_data["current_frame"]]
            x, y = skin_data["position"]
            # Crea il rettangolo per il disegno
            rect = arcade.Rect(
                x - self.width // 2,
                x + self.width // 2,
                y + self.height // 2,
                y - self.height // 2,
                100,
                100,
                x,
                y
            )

            # Disegna la texture all'interno del rettangolo
            arcade.draw_texture_rect(
                texture=frame_texture,
                rect=rect
            )

            # Aggiorna la posizione per la skin successiva
            current_x += 50 + margin



    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from schermate.MenuScreen import MenuScreen
            self.window.show_view(MenuScreen(True))

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.shop.buttons:
            button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.shop.buttons:
                btn.on_click(x, y)