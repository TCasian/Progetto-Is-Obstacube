import arcade
from utils import FadeManager as Fd
from time import sleep

class MenuScreen(arcade.View):
    INTRO, BUTTONS, OUTRO = "intro", "buttons", "outro"

    def __init__(self):
        super().__init__()
        self.state = self.INTRO
        arcade.enable_timings()
        self.fadeManager = Fd.FadeManager(0.005)

    def on_show_view(self):
        """Chiamato solo la prima volta quando viene creata la view"""
        self._configura_stato()



    def _configura_stato(self):
        """Configura le cose base quando si cambia lo stato tipo background musica ecc"""
        if self.state == self.INTRO:
            arcade.set_background_color(arcade.color.BLACK)
            self.fadeManager.start_fade((0, 0, 0, 255), (255, 255, 255, 0))
            arcade.set_background_color(arcade.color.WHITE)
            self.draw_state = self._draw_intro
        elif self.state == self.BUTTONS:
            arcade.set_background_color(arcade.color.LIGHT_BLUE)
            self.draw_state = self._draw_buttons
        elif self.state == self.OUTRO:
            arcade.set_background_color(arcade.color.BLACK)
            self.draw_state = self._draw_outro

    def on_update(self, dt):
        """Chiamato ogni frame per aggiornare la logica dt è deltatime sec dall ultimo frame"""
        self.fadeManager.update()

        arcade.get_timings()
        #print(arcade.get_fps())

    def on_draw(self):
        """Chiamato ogni frame per disegnare la scena"""
        self.clear()
        self.fadeManager.draw()

        self.draw_state()
        #self.fadeManager.draw()


    def on_key_press(self, key, modifiers):
        """Chiamato quando si preme un tasto"""
        if self.state == self.INTRO:
            if key == arcade.key.SPACE:
                print("Passaggio allo stato BUTTONS.")
                self.state = self.BUTTONS
                self._configura_stato()
        elif self.state == self.BUTTONS:
            if key == arcade.key.ESCAPE:
                print("Passaggio allo stato OUTRO.")
                self.state = self.OUTRO
                self._configura_stato()
        elif self.state == self.OUTRO:
            if key == arcade.key.ENTER:
                print("Riavvio allo stato INTRO.")
                self.state = self.INTRO
                self._configura_stato()

    def _draw_intro(self):
        if not self.fadeManager.is_fading:
            arcade.draw_text(
                "INTRO",
                self.window.width / 2, self.window.height / 2,
                arcade.color.BLACK, font_size=30, anchor_x="center"
            )
            #self.state = self.BUTTONS
            #self._configura_stato()

    def _draw_buttons(self):
        arcade.draw_text(
            "BUTTONS",
            self.window.width / 2, self.window.height / 2,
            arcade.color.BLACK, font_size=30, anchor_x="center"
        )

    def _draw_outro(self):
        arcade.draw_text(
            "OUTRO",
            self.window.width / 2, self.window.height / 2,
            arcade.color.WHITE, font_size=30, anchor_x="center"
        )
