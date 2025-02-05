import arcade
from trio import sleep

from Logica.ImpostazioniLogica import ImpostazioniLogica
from Logica.MenuLogica import MenuLogica

class MenuScreen(arcade.View):

    def __init__(self, jump=True):
        super().__init__()
        self.menu = MenuLogica(self.window, jump)

    def on_show_view(self):
        """Chiamato solo la prima volta quando viene creata la view"""
        arcade.set_background_color(arcade.color.WHITE)
        if self.menu._configura_stato():
            self.draw_state = self._draw_intro
        else:
            self.draw_state = self._draw_buttons
        self.scene = arcade.Scene.from_tilemap(arcade.load_tilemap("Media/mappe/Intro.tmx", 1 if not ImpostazioniLogica().is_fullscreen() else 1.3))
        if not self.menu.get_jump():
            self.logo_sprite = arcade.Sprite("Media/Img/Logo.png", 1 if not ImpostazioniLogica().is_fullscreen() else 1.3)

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
        self.menu.create_popup_buttons()
        self.menu.get_popup_buttons()

        for button in self.menu.get_popup_buttons():
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
        self.menu.popup = False
        self.menu.create_close_popup_buttons()
        for button in self.menu.get_close_popup_buttons():
            button.draw()

    def on_update(self, dt):
        """Chiamato ogni frame per aggiornare la logica"""
        self.menu.update_manager()
        self.menu.timing()
        arcade.get_timings()


    def on_draw(self):
        """Chiamato ogni frame per disegnare la scena"""
        self.clear()
        self.menu.get_fade_manager().draw()
        self.draw_state()


        for button in self.menu.get_buttons():
            button.draw()

        if self.menu.get_popup():
            self._draw_popup()

        if self.menu.get_popup_non_disponibile():
            self._draw_popup_non_disponibile()

    def on_mouse_motion(self, x, y, dx, dy):
        """Gestisce il movimento del mouse"""
        if self.menu.get_popup():
            for button in self.menu.get_popup_buttons():
                button.on_hover(x,y)
        else:
            for button in self.menu.get_buttons():
                button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Gestisce il click del mouse"""
        if self.menu.get_popup() or self.menu.get_popup_non_disponibile():
            for btn in self.menu.get_popup_buttons():
                btn.on_click(x, y)
            for btn in self.menu.close_popup_buttons:
                btn.on_click(x, y)
        else:
            for btn in self.menu.get_buttons():
                btn.on_click(x, y)

    def _draw_intro(self):
        if not self.menu.get_fade_manager().is_fading:
            self.logo_sprite.center_x = self.window.width *0.5
            self.logo_sprite.center_y = self.window.height *0.5
            arcade.draw_texture_rect(self.logo_sprite.texture, self.logo_sprite.rect)
            self.menu.set_state(self.menu.BUTTONS)
            self.menu.set_timerIntro(True)
            if self.menu.get_state() == self.menu.INTRO:
                self.draw_state = self._draw_intro
            else:
                self.draw_state = self._draw_buttons

    def _draw_buttons(self):
        """Disegna lo stato BUTTONS"""
        if  not self.menu.get_fade_manager().is_fading:
            self.scene.draw()
            if not self.menu.get_popup():
                for button in self.menu.get_buttons():
                    button.draw()
            else:
                for button in self.menu.get_popup_buttons():
                    button.draw()


