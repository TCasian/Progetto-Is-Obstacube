import arcade
from schermate.ImpostazioniScreen import ImpostazioniScreen
from schermate.MappeScreen import MappeScreen
from schermate.ShopScreen import ShopScreen
from utils import FadeManager as Fd
from utils.RoundedButtons import RoundedButton
from time import sleep

class MenuLogica:
    INTRO, BUTTONS = "intro", "buttons"

    def __init__(self, window, jump):
        self.state = self.BUTTONS if jump else self.INTRO
        self.fadeManager = Fd.FadeManager(0.015)
        self.popup = False
        self.popupNonDisponibile = False
        self.jump = jump
        self.buttons = []
        self.popup_buttons = []
        self.debug = False
        self.window = window
        self.close_popup_buttons = []


    def _create_buttons(self):
        """Crea i bottoni e li aggiunge a Uimanager"""
        button_height = 60
        button_width = 350
        button_spacing = 40

        buttons_data = [
            ("Esci", lambda: arcade.close_window()),
            ("Impostazioni ", lambda: self.window.show_view(ImpostazioniScreen())),
            ("Shop", lambda: self.window.show_view(ShopScreen())),
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

    def get_jump(self):
        return self.jump

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

    def _configura_stato(self):
        """Configura le cose base quando si cambia lo stato tipo background, musica ecc."""
        self.buttons = []# Reset dei bottoni
        if self.state == self.INTRO:
            arcade.set_background_color(arcade.color.WHITE)
            if not self.jump:
                self.fadeManager.start_fade((255, 255, 255, 0), (0, 0, 0, 255))  # Fade da nero a trasparente
            return True
        elif self.state == self.BUTTONS:
            if not self.debug and not self.jump:
                sleep(3)
            self._create_buttons()
            return False

    def create_popup_buttons(self):
        popup_buttons_data = [
            ("Standard", lambda: self.window.show_view(MappeScreen(False))),
            ("AI", lambda: self._on_click_non_disponibile()),
        ]
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

    def get_popup_buttons(self):
        return self.popup_buttons

    def create_close_popup_buttons(self):
        if not any(isinstance(btn, RoundedButton) and btn.text == "X" for btn in self.popup_buttons):
            self.close = RoundedButton(
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
            self.close_popup_buttons.append(self.close)

    def get_close_popup_buttons(self):
        return self.close_popup_buttons

    def update_manager(self):
        self.fadeManager.update()

    def timing(self):
        if hasattr(self, "timerIntro") and self.timerIntro:
            self._configura_stato()
            del self.timerIntro

    def get_fade_manager(self):
        return self.fadeManager

    def get_buttons(self):
        return self.buttons

    def get_popup(self):
        return self.popup

    def get_popup_non_disponibile(self):
        return self.popupNonDisponibile

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_timerIntro(self, timerIntro):
        self.timerIntro = timerIntro