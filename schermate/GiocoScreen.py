import arcade
import time

from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.ImpostazioniScreen import ImpostazioniScreen
from utils.RoundedButtons import RoundedButton
from utils.RectangleBorder import RectangleBorder

TILE_SCALING = 1.0
PLAYER_SPEED = 5
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32

class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = 50
        self.height = 50
        self.color = arcade.color.WHITE
        self.change_x = 0
        self.change_y = 0
        self.max_life = 5
        self.health = 5
        self.coins = 0
        self.last_danno = 0

    def add_health(self, val):
        if ImpostazioniLogica().is_audio():
            sound = arcade.Sound("Media/Sounds/health_up_sound.wav")
            sound.play(volume=0.5)
        temp = self.health + val
        if not temp > self.max_life:
            self.health = temp

    def rem_health(self, val):
        temp = self.health - val
        if not temp < 0 and time.time() - self.last_danno >= 0.3:
            self.health = temp
            self.last_danno = time.time()



    def draw(self):
        immune = (time.time() - self.last_danno <= 0.3)
        self.left = self.center_x - self.width *0.5
        self.right = self.center_x + self.width *0.5
        self.bottom = self.center_y - self.height *0.5
        self.top = self.center_y + self.height *0.5
        color = arcade.color.RED if immune else self.color
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, color)

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def get_surrounding_grid(self, tile_grid, grid_size=10):
        # Trova la posizione del giocatore nella griglia
        player_x = int(self.center_x // TILE_WIDTH)
        player_y = int(self.center_y // TILE_HEIGHT)

        player_width_tiles = int(self.width // TILE_WIDTH)
        player_height_tiles = int(self.height // TILE_HEIGHT)

        half_grid = int(grid_size *0.5)
        start_x = max(0, player_x - half_grid)
        end_x = min(len(tile_grid[0]) - 1, player_x + half_grid)
        start_y = max(0, player_y - half_grid)
        end_y = min(len(tile_grid) - 1, player_y + half_grid)

        grid = []
        for y in range(start_y, end_y + 1):
            row = []
            for x in range(start_x, end_x + 1):
                # Verifica se il giocatore si sovrappone a questo tile
                if (player_x <= x < player_x + player_width_tiles and
                    player_y <= y < player_y + player_height_tiles):
                    row.append("PLAYER")
                else:
                    row.append(tile_grid[y][x])
            grid.append(row)

        return grid


class GiocoScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.cuoriList = []
        self.moneteList = []
        self.tilemap = arcade.load_tilemap("Media/mappe/mappa1.tmx", TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

        self.ostacoli = self.scene["ostacoli"] if "ostacoli" in self.scene else arcade.SpriteList()
        self.bombe = self.scene["bombe"] if "bombe" in self.scene else arcade.Sprite()

        self.monete = self.scene["monete"] if "monete" in self.scene else arcade.SpriteList()
        self.monete.rescale(1.3)

        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()
        self.cuore_pieno_sprite = arcade.Sprite("Media/img/cuore_pieno.png", scale=1.3)
        self.cuore_vuoto_sprite = arcade.Sprite("Media/img/cuore_vuoto.png", scale=1.3)

        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()

        self.monete.rescale(1.3)
        self.player = Player(150, 300)
        self.start_time = time.time()

        self.camera = arcade.camera.Camera2D()
        self.tile_grid = self._build_tile_grid()
        self.start_pause = 0


        self.finish = None

    def on_show_view(self):
        self.camera =arcade.camera.Camera2D()
        self._create_buttons()
        self.tilemap = arcade.load_tilemap("Media/mappe/mappa1.tmx",
                                           TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

        self.ostacoli = self.scene["ostacoli"] if "ostacoli" in self.scene else arcade.SpriteList()
        self.bombe = self.scene["bombe"] if "bombe" in self.scene else arcade.Sprite()

        self.monete = self.scene["monete"] if "monete" in self.scene else arcade.SpriteList()
        self.monete.rescale(1.3)

        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()
        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()
        self.scaling = TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3
        for moneta in list(self.monete):
            posizione = (round(moneta.center_x/self.scaling), round(moneta.center_y/self.scaling))
            if posizione in self.moneteList:
                moneta.remove_from_sprite_lists()
        for cuore in list(self.cuori):
            posizione = (round(cuore.center_x / self.scaling), round(cuore.center_y / self.scaling))
            if posizione in self.cuoriList:
                cuore.remove_from_sprite_lists()
        self.player.center_x = round(self.playerposition_x * self.scaling)
        self.player.center_y = round(self.playerposition_y * self.scaling)


    def on_draw(self):
        self.clear()
        self.camera.use()

        self.scene.draw()
        self.player.draw()

        if not self.finish:
            self._draw_info()
        else:
            self._draw_finish()
        if self.start_pause != 0:
            self._draw_paused()



    def on_mouse_motion(self, x, y, dx, dy):
        print()
        if self.start_pause != 0:
            for button in self.paused_buttons:
                button.on_hover(x, y)
        elif self.finish == "Gameover":
            for button in self.finish_buttons_gameover:
                button.on_hover(x, y)
        elif self.finish == "Win":
            for button in self.finish_buttons_win:
                button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
       if self.start_pause != 0:
            for button in self.paused_buttons:
                button.on_click(x, y)
       elif self.finish == "Gameover":
           for button in self.finish_buttons_gameover:
               button.on_click(x, y)
       elif self.finish == "Win":
           for button in self.finish_buttons_win:
               button.on_click(x, y)


    def on_update(self, delta_time):
        if self.start_pause != 0 or self.finish is not None:
            return

        self.player.update()

        oggetti_colpiti = {
            "ostacoli": arcade.check_for_collision_with_list(self.player, self.ostacoli),
            "monete": arcade.check_for_collision_with_list(self.player, self.monete),
            "cuori": arcade.check_for_collision_with_list(self.player, self.cuori),
            "danni": arcade.check_for_collision_with_list(self.player, self.danni)
        }

        if oggetti_colpiti["ostacoli"]:
            self.player.center_x -= self.player.change_x
            self.player.center_y -= self.player.change_y

        for moneta in oggetti_colpiti["monete"]:
            self.moneteList.append((round(moneta.center_x/self.scaling), round(moneta.center_y/self.scaling)))
            moneta.remove_from_sprite_lists()
            self.player.coins += 1
            if ImpostazioniLogica().is_audio():
                sound = arcade.Sound("Media/Sounds/coin_sound.mp3")
                sound.play(volume=0.5)
            self.tile_grid = self._build_tile_grid()
            print(f"Moneta raccolta! Monete totali: {self.player.coins}")

        for cuore in oggetti_colpiti["cuori"]:
            self.cuoriList.append((round(cuore.center_x/self.scaling), round(cuore.center_y/self.scaling)))
            cuore.remove_from_sprite_lists()
            self.player.add_health(1)
            self.tile_grid = self._build_tile_grid()
            print(f"Vita raccolta! Vita attuale: {self.player.health}")

        if oggetti_colpiti["danni"]:
            self.player.rem_health(1)
            if ImpostazioniLogica().is_audio():
                sound = arcade.Sound("Media/Sounds/health_down_sound.mp3")
                sound.play(volume=0.5)
            if self.player.health <= 0:
                self.finish = "Gameover"

        self.scene.update_animation(delta_time)
        self._muovi_camera()

    def print_player_grid(self):
        """
        Stampa una porzione della griglia centrata sul giocatore.
        """
        grid = self.player.get_surrounding_grid(self.tile_grid, grid_size=10)

        print("\nGriglia centrata sul giocatore:")
        for row in grid[::-1]:
            print(row)
        print("\n")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player.change_y = PLAYER_SPEED
        elif key == arcade.key.S:
            self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.A:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.ESCAPE:
            if self.finish == "Gameover":
                pass
            elif self.start_pause == 0:
                self.playerposition_x = round(self.player.center_x / self.scaling)
                self.playerposition_y = round(self.player.center_y / self.scaling)
                self.start_pause = time.time()
            else:
                self.start_time += int(time.time() - self.start_pause)
                self.start_pause = 0


        elif key == arcade.key.SPACE:
            self.print_player_grid()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        elif key in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0

    def _build_tile_grid(self):
        grid = [["[]" for _ in range(self.tilemap.width)] for _ in range(self.tilemap.height)]

        for sprites in [self.ostacoli, self.monete, self.cuori, self.danni]:
            for sprite in sprites:
                x = int(sprite.center_x // self.tilemap.tile_width)
                y = int(sprite.center_y // self.tilemap.tile_height)
                if 0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height:
                    grid[y][x] = sprite.properties.get("tipo", "diocane")

        return grid

    def _create_buttons(self):
        button_height = 60
        button_width = 350
        button_spacing = 30
        buttons_data = [
            ("Torna al menu ", lambda:  self._go_menu()),
            ("Come giocare ", lambda: print("aa")),
            ("Impostazioni ", lambda: self.window.show_view(ImpostazioniScreen(self._return))),
            ("Torna al gioco ", lambda: setattr(self, "start_pause", 0)),

        ]

        start_y = self.window.height - 540

        self.paused_buttons = []
        self.finish_buttons_gameover = []
        self.finish_buttons_win = []

        for i, (label, callback) in enumerate(buttons_data):
            x = self.camera.position[0]
            y = start_y + i * (button_height + button_spacing)

            button = RoundedButton(
                text=label,
                center_x=x,
                center_y=y,
                width=button_width,
                height=button_height,
                bg_color=(240,255,240),
                bg_hover=(217, 147, 8),
                text_color=arcade.color.BLACK,
                text_size=20,
                hover_text_color=arcade.color.WHITE,
                callback=callback,
                bold=True
            )
            self.paused_buttons.append(button)

        self.finish_buttons_gameover.append(RoundedButton(
            text="Riprova!",
            center_x=self.camera.position[0] - 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback=lambda: self.window.show_view(GiocoScreen()),
            bold=True
        ))

        self.finish_buttons_gameover.append(RoundedButton(
            text="Torna al menu!",
            center_x=self.camera.position[0] + 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback= lambda: self._go_menu(),
            bold=True
        ))

    def _muovi_camera(self):
        screen_center_x = self.player.center_x - (self.window.width *0.5)
        screen_center_y = self.window.height *0.5

        if screen_center_x < 0:
            screen_center_x = 0

        map_width = self.tilemap.width * self.tilemap.tile_width
        if screen_center_x > map_width - self.window.width:
            screen_center_x = map_width - self.window.width

        if self.player.center_x > self.window.width *0.5:
            self.camera.position = (screen_center_x + self.window.width *0.5, screen_center_y)
        self._aggiorna_posizione_pulsanti()

    def _aggiorna_posizione_pulsanti(self):
        start_y = self.window.height - 540

        for i, button in enumerate(self.paused_buttons):
            button.center_x = self.camera.position[0]
            button.center_y = start_y + i * (button.height + 30)

        self.finish_buttons_gameover[0].center_x = self.camera.position[0] - 200
        self.finish_buttons_gameover[1].center_x = self.camera.position[0] + 200


        self.finish_buttons_gameover[0].center_y = self.camera.position[1] - 200
        self.finish_buttons_gameover[1].center_y = self.camera.position[1] - 200

        for button in self.finish_buttons_win:
            button.center_x = self.camera.position[0] + 200
            button.center_y = self.camera.position[1] - 200

    def _draw_info(self):
        tempo_width, tempo_height = 300, 120
        cuori_width, cuori_height = 250, 70
        soldi_width, soldi_height = 250, 70

        y_offset = self.window.height - 30

        cuori_x = self.camera.position[0] - tempo_width *0.5 - cuori_width *0.5 + 5
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

        for i in range(self.player.max_life):
            if i < self.player.health:
                self.cuore_pieno_sprite.center_x = start_x + i * (self.cuore_pieno_sprite.width + spacing)
                self.cuore_pieno_sprite.center_y = cuori_y + (cuori_height - self.cuore_pieno_sprite.height) *0.5 - 10
                arcade.draw_texture_rect(self.cuore_pieno_sprite.texture, self.cuore_pieno_sprite.rect)
            else:
                self.cuore_vuoto_sprite.center_x = start_x + i * (self.cuore_vuoto_sprite.width + spacing)
                self.cuore_vuoto_sprite.center_y = cuori_y + (cuori_height - self.cuore_vuoto_sprite.height) *0.5 - 10
                arcade.draw_texture_rect(self.cuore_vuoto_sprite.texture, self.cuore_vuoto_sprite.rect)

        soldi_x = self.camera.position[0] + tempo_width *0.5 + soldi_width *0.5 - 5
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
            f"{self.player.coins}",
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
            self.camera.position[0],
            tempo_y,
            tempo_width,
            tempo_height,
            bg_color=(217, 147, 8),
        )
        tempo.draw()


        if self.start_pause == 0:
            self.tempo_trascorso =  int(time.time() - self.start_time)
        minuti =  self.tempo_trascorso  // 60
        secondi = self.tempo_trascorso % 60

        tempo_testo = f"{minuti:02}:{secondi:02}"
        arcade.draw_text(
            tempo_testo,
            self.camera.position[0]-75,
            tempo_y - 20,
            arcade.color.WHITE,
            font_size=50,
            bold=True
        )

    def _draw_paused(self):
        y_offset= self.window.height - 30
        pausa_width, pausa_height = 800 - 8, 500
        pausa_x = self.camera.position[0]
        pausa_y = y_offset - pausa_height + 120
        tempo = RectangleBorder(
            pausa_x,
            pausa_y,
            pausa_width,
            pausa_height,
            bg_color=(217, 147, 8),
        )
        tempo.draw()

        for button in self.paused_buttons:
            button.draw()

    def _draw_finish(self):
        y_offset = self.window.height - 30
        pausa_width, pausa_height = 800 - 8, 520
        pausa_x = self.camera.position[0]
        pausa_y = y_offset - pausa_height + 120
        tempo = RectangleBorder(
            pausa_x,
            pausa_y,
            pausa_width,
            pausa_height,
            bg_color=(217, 147, 8),
        )
        tempo.draw()
        if self.finish == "Gameover":
            arcade.draw_text(
                "Sei morto!",
                self.camera.position[0] - 120,
                self.camera.position[1] + 100,
                arcade.color.RED,
                font_size=45,
                bold=True
            )

            minuti = self.tempo_trascorso // 60
            secondi = self.tempo_trascorso % 60

            tempo= f"{minuti:02}:{secondi:02}"
            arcade.draw_text(
                "Tempo : "+tempo,
                self.camera.position[0] - 160,
                self.camera.position[1] + 20,
                arcade.color.WHITE,
                font_size=45,
                bold=True
            )

            arcade.draw_text(
                f"Hai raccolto {self.player.coins} monete! (perse)",
                self.camera.position[0] - 380,
                self.camera.position[1] - 60,
                arcade.color.WHITE,
                font_size=45,
                bold=True
            )

            for button in self.finish_buttons_gameover:
                button.draw()


        if self.finish == "win":
            print("Win")

    def _go_menu(self):
        from schermate.MenuScreen import MenuScreen
        self.camera.position =(self.window.width *0.5, self.window.height *0.5)
        self.camera.use()
        self.window.show_view(MenuScreen(True))

    def _return(self):
        self.window.show_view(self)
