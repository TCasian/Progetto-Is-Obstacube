import arcade
import time

from Logica.GiocoAI import GiocoLogica
from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.ImpostazioniScreen import ImpostazioniScreen
from utils.RoundedButtons import RoundedButton
from utils.RectangleBorder import RectangleBorder
from Logica.PlayerLogica import Player

TILE_SCALING = 1.0
PLAYER_SPEED = 5
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32

class GiocoScreen(arcade.View):
    def __init__(self, mappa="test.tmx", training_mode=False):
        super().__init__()
        self.training_mode = training_mode
        self.gioco = GiocoLogica(self.window, mappa, self, training_mode)
        self.flag = False
        self.key = 4

    def on_show_view(self):
        self.gioco.camera = arcade.camera.Camera2D()
        self.gioco._create_buttons()
        self.gioco.load_map()
        self.gioco.resize()

    def on_draw(self):
        self.clear()
        self.gioco.camera.use()

        self.gioco.scene.draw()
        self.gioco.player.draw()

        if not self.gioco.finish:
            self._draw_info()
        if self.gioco.start_pause != 0:
            self._draw_paused()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.gioco.start_pause != 0:
            for button in self.gioco.paused_buttons:
                button.on_hover(x, y)
        elif self.gioco.finish == "Gameover":
            for button in self.gioco.finish_buttons_gameover:
                button.on_hover(x, y)
        elif self.gioco.finish == "Win":
            for button in self.gioco.finish_buttons_win:
                button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
       if self.gioco.start_pause != 0:
            for button in self.gioco.paused_buttons:
                button.on_click(x, y)
       elif self.gioco.finish == "Gameover":
           for button in self.gioco.finish_buttons_gameover:
               button.on_click(x, y)
       elif self.gioco.finish == "Win":
           for button in self.gioco.finish_buttons_win:
               button.on_click(x, y)


    def on_update(self, delta_time):
        if self.training_mode and not self.flag:
            self.flag = True
            self.train_gen = self.gioco.train_episode()

        if self.training_mode:
            try:
                # Esegue un passo dell'addestramento
                next(self.train_gen)
            except StopIteration:
                # Ricomincia un nuovo episodio
                self.train_gen = self.gioco.train_episode()
            # Per visualizzare l'addestramento



    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.gioco.player.change_y = PLAYER_SPEED*3
            self.key = 2
        elif key == arcade.key.S:
            self.gioco.player.change_y = -PLAYER_SPEED*3
            self.key = 3
        elif key == arcade.key.A:
            self.gioco.player.change_x = -PLAYER_SPEED*3
            self.key = 0
        elif key == arcade.key.D:
            self.gioco.player.change_x = PLAYER_SPEED*3
            self.key = 1
        elif key == arcade.key.ESCAPE:
            self.gioco.pausa()
        elif key == arcade.key.SPACE:
            self.gioco.print_player_grid()
        elif key == arcade.key.Z:
            self.gioco.flag = not self.gioco.flag

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.gioco.player.change_y = 0
        elif key in (arcade.key.A, arcade.key.D):
            self.gioco.player.change_x = 0

    def _draw_info(self):
        tempo_width, tempo_height = 300, 120
        cuori_width, cuori_height = 250, 70
        soldi_width, soldi_height = 250, 70

        y_offset = self.window.height - 30

        cuori_x = self.gioco.camera.position[0] - tempo_width *0.5 - cuori_width *0.5 + 5
        cuori_y = y_offset - cuori_height *0.5 - 25
        cuori = RectangleBorder(
            cuori_x,
            cuori_y,
            cuori_width,
            cuori_height,
            bg_color=(217, 147, 8),
        )
        cuori.draw()


        spacing = 1
        start_x = cuori_x - cuori_width *0.5 + 38

        for i in range(self.gioco.player.max_life):
            if i < self.gioco.player.health:
                self.gioco.cuore_pieno_sprite.center_x = start_x + i * (self.gioco.cuore_pieno_sprite.width + spacing)
                self.gioco.cuore_pieno_sprite.center_y = cuori_y + (cuori_height - self.gioco.cuore_pieno_sprite.height) *0.5 - 10
                arcade.draw_texture_rect(self.gioco.cuore_pieno_sprite.texture, self.gioco.cuore_pieno_sprite.rect)
            else:
                self.gioco.cuore_vuoto_sprite.center_x = start_x + i * (self.gioco.cuore_vuoto_sprite.width + spacing)
                self.gioco.cuore_vuoto_sprite.center_y = cuori_y + (cuori_height - self.gioco.cuore_vuoto_sprite.height) *0.5 - 10
                arcade.draw_texture_rect(self.gioco.cuore_vuoto_sprite.texture, self.gioco.cuore_vuoto_sprite.rect)

        soldi_x = self.gioco.camera.position[0] + tempo_width *0.5 + soldi_width *0.5 - 5
        soldi_y = y_offset - soldi_height *0.5 - 25
        soldi = RectangleBorder(
            soldi_x,
            soldi_y,
            soldi_width,
            soldi_height,
            bg_color=(217, 147, 8),
        )
        soldi.draw()

        arcade.draw_text(
            f"{self.gioco.player.coins}",
            soldi_x - (soldi_width *0.25) - 35,
            soldi_y - soldi_height *0.5 + 25,
            arcade.color.WHITE,
            font_size=24,
            bold=True
        )

        moneta_sprite = arcade.Sprite("Media/img/coin.png", scale=1.2)
        moneta_sprite.center_x = soldi_x - (soldi_width *0.25) + 20
        moneta_sprite.center_y = soldi_y
        arcade.draw_texture_rect(moneta_sprite.texture, moneta_sprite.rect)

        #tempo_x = self.camera.position[0]
        tempo_y = y_offset - tempo_height *0.5
        tempo = RectangleBorder(
            self.gioco.camera.position[0],
            tempo_y,
            tempo_width,
            tempo_height,
            bg_color=(217, 147, 8),
        )
        tempo.draw()


        if self.gioco.start_pause == 0:
            self.tempo_trascorso =  int(time.time() - self.gioco.start_time)
        minuti =  self.tempo_trascorso  // 60
        secondi = self.tempo_trascorso % 60

        tempo_testo = f"{minuti:02}:{secondi:02}"
        arcade.draw_text(
            tempo_testo,
            self.gioco.camera.position[0]-75,
            tempo_y - 20,
            arcade.color.WHITE,
            font_size=50,
            bold=True
        )

    def _draw_paused(self):
        y_offset= self.window.height - 30
        pausa_width, pausa_height = 800 - 8, 500
        pausa_x = self.gioco.camera.position[0]
        pausa_y = y_offset - pausa_height + 120
        tempo = RectangleBorder(
            pausa_x,
            pausa_y,
            pausa_width,
            pausa_height,
            bg_color=(217, 147, 8),
        )
        tempo.draw()

        for button in self.gioco.paused_buttons:
            button.draw()


    def _return(self):
        self.window.show_view(self)

    def get_key(self):
        return self.key