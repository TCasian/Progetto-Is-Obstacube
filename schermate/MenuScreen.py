import arcade
from arcade import SpriteList
from arcade.gui import UIManager, UIFlatButton

from Logica.ImpostazioniLogica import ImpostazioniLogica
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

    def __init__(self, jump=True):
        super().__init__()
        self.state = self.BUTTONS if jump else self.INTRO
        self.fadeManager = Fd.FadeManager(0.015)
        self.popup = False
        self.popupNonDisponibile = False
        self.buttons = []
        self.popup_buttons = []
        self.debug = False
        self.jump = jump


    def on_show_view(self):
        """Chiamato solo la prima volta quando viene creata la view"""
        self._configura_stato()

        self.scene = arcade.Scene.from_tilemap(arcade.load_tilemap("Media/mappe/Intro.tmx", 1 if not ImpostazioniLogica().is_fullscreen() else 1.3))
        if not self.jump:
            self.logo_sprite = arcade.Sprite("Media/Img/Logo.png", 1 if not ImpostazioniLogica().is_fullscreen() else 1.3)
        self.window.show_view(GiocoScreen("mappa1.tmx"))


    def _configura_stato(self):
        """Configura le cose base quando si cambia lo stato tipo background, musica ecc."""
        self.buttons = []  # Reset dei bottoni

        if self.state == self.INTRO:
            arcade.set_background_color(arcade.color.WHITE)
            if not self.jump:
                self.fadeManager.start_fade((255, 255, 255, 0), (0, 0, 0, 255))  # Fade da nero a trasparente
            self.draw_state = self._draw_intro
        elif self.state == self.BUTTONS:
            if not self.debug and not self.jump:
                sleep(3)
            self._create_buttons()
            self.draw_state = self._draw_buttons

    def _create_buttons(self):
        """Crea i bottoni e li aggiunge a Uimanager"""
        button_height = 60
        button_width = 350
        button_spacing = 40

        buttons_data = [
            ("Esci ", lambda: arcade.exit()),
            ("Impostazioni ", lambda: self.window.show_view(ImpostazioniScreen())),
            ("Shop", lambda: self._on_click_non_disponibile()),
            ("Mappe ", lambda: self.window.show_view(MappeScreen())),
            ("Gioca ", lambda: self._on_click_gioca()),

        ]

        total_height = len(buttons_data) * (button_height + button_spacing)
        start_y = (self.window.height - total_height) *0.5 + 50

        for i, (label, callback) in enumerate(buttons_data):
            x = self.window.width * 0.5
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
        popup_width = self.window.width *0.5 - 100
        popup_height = self.window.height *0.5 - 120
        left = (self.window.width - popup_width) *0.5
        right = left + popup_width
        bottom = (self.window.height - popup_height) *0.5
        top = bottom + popup_height

        # Disegna lo sfondo del popup
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.WHITE)

        popup_buttons_data = [
                ("Standard", lambda: self.window.show_view(MappeScreen(False))),
                ("AI", lambda: print("AI")),
            ]

        self.popup_buttons = []
        button_height = 50
        button_spacing = 40
        start_y = (self.window.height // 2) - (len(popup_buttons_data) * (button_height + button_spacing)) // 2 + 50

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

    def _draw_popup_non_disponibile(self):
        left = self.window.width *0.25
        right = self.window.width * 3 *0.25
        bottom = self.window.height *0.25
        top = self.window.height * 3 *0.25

        x = self.window.width *0.5
        y = self.window.height *0.5
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.WHITE)
        arcade.draw_text("Sezione non disponibile", x, y, arcade.color.ORANGE, font_size=30, anchor_x="center")
        if not any(isinstance(btn, RoundedButton) and btn.text == "X" for btn in self.popup_buttons):
            self.close_popup_button = RoundedButton(
                text="X",
                center_x=self.window.width * 3 *0.25 - 20,
                center_y=self.window.height * 3 *0.25 - 20,
                width=40,
                height=40,
                bg_color=(200, 0, 0),
                bg_hover=(255, 50, 50),
                text_color=arcade.color.WHITE,
                text_size=20,
                hover_text_color=arcade.color.WHITE,
                callback=self._close_non_disponibile_popup,
                bold=True
            )
            self.popup_buttons.append(self.close_popup_button)

        for button in self.popup_buttons:
            button.draw()


    def _on_click_gioca(self):
        """Callback per il bottone 'Gioca'"""
        self.popup = True

    def _on_click_non_disponibile(self):
        """Callback per il bottone 'Mappe'"""
        if not self.popupNonDisponibile:
            self.popupNonDisponibile = True

    def _close_non_disponibile_popup(self):
        """Chiude il popup delle mappe."""
        self.popupNonDisponibile = False

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

        if self.popupNonDisponibile:
            self._draw_popup_non_disponibile()

    def on_mouse_motion(self, x, y, dx, dy):
        """Gestisce il movimento del mouse"""
        if self.popup:
            for button in self.popup_buttons:
                print(button.on_hover(x,y))
        else:
            for button in self.buttons:
                button.on_hover(x, y)


    def on_mouse_press(self, x, y, button, modifiers):
        """Gestisce il click del mouse"""
        if self.popup or self.popupNonDisponibile:
            for btn in self.popup_buttons:
                btn.on_click(x, y)
        else:
            for btn in self.buttons:
                btn.on_click(x, y)

    def _draw_intro(self):

        if not self.fadeManager.is_fading:
            self.logo_sprite.center_x = self.window.width *0.5
            self.logo_sprite.center_y = self.window.height *0.5
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
            else:
                for button in self.popup_buttons:
                    button.draw()

    def _go_to_menu(self):
        self.window.show_view(self)

