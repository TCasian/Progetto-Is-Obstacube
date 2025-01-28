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

class MenuScreen(arcade.View):
    INTRO, BUTTONS= "intro", "buttons"

    def __init__(self):
        super().__init__()
        self.state = self.INTRO
        arcade.enable_timings()
        self.fadeManager = Fd.FadeManager(0.015)
        self.popup = False
        self.ui_manager = UIManager()


    def on_show_view(self):
        """Chiamato solo la prima volta quando viene creata la view"""
        self._configura_stato()
        map_file = "Media/mappe/mappa_intro.tmx"
        self.tile_map = arcade.load_tilemap(map_file, scaling=1.0)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.logo_sprite = arcade.Sprite("Media/Img/Logo.png", 1)

    def _configura_stato(self):
        """Configura le cose base quando si cambia lo stato tipo background musica ecc"""
        self.ui_manager.clear()

        if self.state == self.INTRO:
            arcade.set_background_color(arcade.color.WHITE)
            self.fadeManager.start_fade((255, 255, 255, 0), (0, 0, 0, 255))  # Fade da nero a trasparente
            self.draw_state = self._draw_intro
        elif self.state == self.BUTTONS:
            sleep(4)
            self.draw_state = self._draw_buttons


    def _draw_popup(self):
        self.ui_manager.clear()
        left = self.window.width // 4
        right = self.window.width * 3 // 4
        bottom = self.window.height // 4
        top = self.window.height * 3 // 4

        color = arcade.color.WHITE
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
        buttons = [
            ("Standard", lambda : self.window.show_view(GiocoScreen())),
            ("AI", lambda : self.window.show_view(AiScreen())),
        ]
        button_height = 50
        total_height = button_height * len(buttons)
        start_y = (self.window.height - total_height) // 2

        for i, (label, callback) in enumerate(buttons):
            x = self.window.width // 2 - 125
            button = UIFlatButton(
                text=label,
                x=x,
                y=start_y + i * (button_height + 30),
                width=250,
            )
            button.on_click = callback
            self.ui_manager.add(button)

    def _create_buttons(self):
        """Crea i bottoni per lo stato BUTTONS"""
        buttons = [
            ("Esci ", lambda: arcade.exit()),
            ("Impostazioni ", lambda: self.window.show_view(SettingsScreen())),
            ("Shop", lambda: self.window.show_view(ShopScreen())),
            ("Mappe ", lambda: self.window.show_view(MappeScreen())),
            ("Gioca ", lambda:  self._on_click_gioca()),

        ]

        button_height = 50
        total_height = button_height * len(buttons)
        start_y = (self.window.height - total_height) // 2

        for i, (label, callback) in enumerate(buttons):
            x  =self.window.width // 2 - 125
            button = UIFlatButton(
                text=label,
                x=x,
                y=start_y + i * (button_height + 30),
                width=250,
            )
            button.on_click = callback
            self.ui_manager.add(button)

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
        self.ui_manager.draw()


    def on_key_press(self, key, modifiers):
        pass

    def on_mouse_press(self, x, y, premuto, modifiers):

        print(f"{x} - {y} - {premuto}- {modifiers}")

        if not self.fadeManager.is_fading:
            for buttons in self.ui_manager.children.values():
                for button in buttons:
                    # Verifica se il mouse è dentro i limiti del bottone
                    if (button.rect.left <= x <= button.rect.right) and (button.rect.bottom <= y <= button.rect.top):
                        print(f"Bottone premuto: {button.text}")
                        button.on_click()

    def _draw_intro(self):
        """Disegna lo stato INTRO"""
        print("Intro")
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
            if self.popup:
                self._draw_popup()
            else:
                self._create_buttons()


    def _on_click_gioca(self):
        """Callback per il bottone 'Gioca'"""
        print("gioca premuto")
        self.popup = True
