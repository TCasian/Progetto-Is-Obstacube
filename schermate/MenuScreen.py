import arcade
from arcade import SpriteList
from arcade.gui import UIManager, UIFlatButton
from schermate.AiScreen import AiScreen
from schermate.GiocoScreen import GiocoScreen
from schermate.MappeScreen import MappeScreen
from schermate.ShopScreen import ShopScreen
from utils import FadeManager as Fd
from time import sleep
from schermate.ImpostazioniScreen import ImpostazioniScreen
from utils.RoundedButtons import RoundedButton


class MenuScreen(arcade.View):
    INTRO, BUTTONS = "intro", "buttons"

    def __init__(self):
        super().__init__()
        self.state = self.INTRO
        arcade.enable_timings()
        self.fadeManager = Fd.FadeManager(0.015)
        self.popup = False
        self.buttons = []
        self.popup_buttons = []
        self.debug = False

    def on_show_view(self):
        """Chiamato solo la prima volta quando viene creata la view"""
        self._configura_stato()

        # Carica la mappa
        self.scene = arcade.Scene.from_tilemap(arcade.load_tilemap("Media/mappe/mappa_intro.tmx", scaling=1.0))

        # Carica il logo
        self.logo_sprite = arcade.Sprite("Media/Img/Logo.png", 1)

    def _configura_stato(self):
        """Configura le cose base quando si cambia lo stato tipo background, musica ecc."""
        self.buttons = []  # Reset dei bottoni

        if self.state == self.INTRO:
            arcade.set_background_color(arcade.color.WHITE)
            self.fadeManager.start_fade((255, 255, 255, 0), (0, 0, 0, 255))  # Fade da nero a trasparente
            self.draw_state = self._draw_intro
        elif self.state == self.BUTTONS:
            if not self.debug:
                sleep(4)
            self._create_buttons()
            self.draw_state = self._draw_buttons

    def _create_buttons(self):
        """Crea i bottoni e li aggiunge a Uimanager"""
        button_height = 50
        button_width = 250
        button_spacing = 30

        buttons_data = [
            ("Esci ", lambda: arcade.exit()),
            ("Impostazioni ", lambda: self.window.show_view(ImpostazioniScreen())),
            ("Shop", lambda: self.window.show_view(ShopScreen())),
            ("Mappe ", lambda: self.window.show_view(MappeScreen())),
            ("Gioca ", lambda: self._on_click_gioca()),

        ]

        total_height = len(buttons_data) * (button_height + button_spacing)
        start_y = (self.window.height - total_height) // 2

        for i, (label, callback) in enumerate(buttons_data):
            x = self.window.width // 2
            y = start_y + i * (button_height + button_spacing)

            button = RoundedButton(
                text=label,
                center_x=x,
                center_y=y,
                width=button_width,
                height=button_height,
                bg_color=(217, 147, 8),
                bg_hover=(247, 178, 38),
                text_color=arcade.color.WHITE,
                text_size=20,
                hover_text_color=arcade.color.WHITE,
                callback=callback,
                bold=True
            )


            self.buttons.append(button)

    def _draw_popup(self):
        """Disegna il popup sopra il menu"""
        left = self.window.width // 4
        right = self.window.width * 3 // 4
        bottom = self.window.height // 4
        top = self.window.height * 3 // 4

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.WHITE)

        popup_buttons_data = [
            ("Standard", lambda: print("Standard")),
            ("AI", lambda: print("AI")),
        ]

        self.popup_buttons = []
        button_height = 50
        button_spacing = 20
        start_y = (self.window.height // 2) - (len(popup_buttons_data) * (button_height + button_spacing)) // 2

        for i, (label, callback) in enumerate(popup_buttons_data):
            x = self.window.width // 2
            y = start_y + i * (button_height + button_spacing)

            button = RoundedButton(
                text=label,
                center_x=x,
                center_y=y,
                width=250,
                height=button_height,
                bg_color=(217, 147, 8),
                bg_hover=(247, 178, 38),
                text_color=arcade.color.WHITE,
                text_size=20,
                hover_text_color=arcade.color.WHITE,
                callback=callback,
                bold=True
            )

            self.popup_buttons.append(button)

        for button in self.popup_buttons:
            button.draw()

    def _on_click_gioca(self):
        """Callback per il bottone 'Gioca'"""
        self.popup = True

    def on_update(self, dt):
        """Chiamato ogni frame per aggiornare la logica"""
        self.fadeManager.update()
        if hasattr(self, "timerIntro") and self.timerIntro:
            self._configura_stato()
            del self.timerIntro
        arcade.get_timings()

    def on_draw(self):
        """Chiamato ogni frame per disegnare la scena"""
        self.clear()
        self.fadeManager.draw()
        self.draw_state()

        for button in self.buttons:
            button.draw()

        if self.popup:
            self._draw_popup()

    def on_mouse_motion(self, x, y, dx, dy):
        """Gestisce il movimento del mouse"""
        if self.popup:
            for button in self.popup_buttons:
                button.on_hover(x,y)
        else:
            for button in self.buttons:
                button.on_hover(x, y)


    def on_mouse_press(self, x, y, button, modifiers):
        """Gestisce il click del mouse"""
        if self.popup:
            for btn in self.popup_buttons:
                btn.on_click(x, y)
        else:
            for btn in self.buttons:
                btn.on_click(x, y)

    def _draw_intro(self):
        """Disegna lo stato INTRO"""
        if not self.fadeManager.is_fading:
            self.logo_sprite.center_x = self.window.width / 2
            self.logo_sprite.center_y = self.window.height / 2
            arcade.draw_texture_rect(self.logo_sprite.texture, self.logo_sprite.rect)
            self.state = self.BUTTONS
            self.timerIntro = True

    def _draw_buttons(self):
        """Disegna lo stato BUTTONS"""
        if not self.fadeManager.is_fading:
            self.scene.draw()
            if not self.popup:
                for button in self.buttons:
                    button.draw()
