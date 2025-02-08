import time

import arcade

from Logica.ImpostazioniLogica import ImpostazioniLogica
from Logica.PlayerLogica import Player
from schermate.ImpostazioniScreen import ImpostazioniScreen
from utils.RoundedButtons import RoundedButton

TILE_SCALING = 1.0
PLAYER_SPEED = 10
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32

class GiocoLogica:
    def __init__(self, window, mappa, view):
        self.camera = arcade.camera.Camera2D()
        self.window = window
        self.view = view
        self.mappa = mappa
        self.tilemap = None
        self.load_map()
        self.load()
        self.cuoriList = []
        self.moneteList = []
        self.playerposition_x = 150
        self.playerposition_y = 300
        self.player = Player(150, 300)
        self.start_time = time.time()
        self.tile_grid = self._build_tile_grid()
        self.start_pause = 0
        self.saved = False
        self.finish = None


    def load_map(self):
        self.tilemap = arcade.load_tilemap(f"Media/mappe/{self.mappa}",TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.ostacoli = self.scene["ostacoli"] if "ostacoli" in self.scene else arcade.SpriteList()
        self.bombe = self.scene["bombe"] if "bombe" in self.scene else arcade.Sprite()
        self.monete = self.scene["monete"] if "monete" in self.scene else arcade.SpriteList()
        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()
        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()

    def load(self):
        self.monete.rescale(1.3)
        self.cuore_pieno_sprite = arcade.Sprite("Media/img/cuore_pieno.png", scale=1.3)
        self.cuore_vuoto_sprite = arcade.Sprite("Media/img/cuore_vuoto.png", scale=1.3)

    def resize(self):
        self.monetepos = []
        for moneta in self.monete:
            self.monetepos.append((moneta.center_x, moneta.center_y))
        self.monete.rescale(1.3)
        for moneta, pos in zip(self.monete, self.monetepos):
            moneta.center_x, moneta.center_y = pos
        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()
        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()
        self.scaling = TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3
        for moneta in list(self.monete):
            posizione = (round(moneta.center_x / self.scaling), round(moneta.center_y / self.scaling))
            if posizione in self.moneteList:
                moneta.remove_from_sprite_lists()
        for cuore in list(self.cuori):
            posizione = (round(cuore.center_x / self.scaling), round(cuore.center_y / self.scaling))
            if posizione in self.cuoriList:
                cuore.remove_from_sprite_lists()
        self.player.center_x = round(self.playerposition_x * self.scaling)
        self.player.center_y = round(self.playerposition_y * self.scaling)

    def print_player_grid(self):
        """
        Stampa una porzione della griglia centrata sul giocatore.
        """
        grid = self.player.get_surrounding_grid(self.tile_grid, grid_size=10)

        print("\nGriglia centrata sul giocatore:")
        for row in grid[::-1]:
            print(row)
        print("\n")

    def _build_tile_grid(self):
        grid = [[0 for _ in range(self.tilemap.width)] for _ in range(self.tilemap.height)]

        for sprites in [self.ostacoli, self.monete, self.cuori, self.danni]:
            for sprite in sprites:
                x = int(sprite.center_x // self.tilemap.tile_width)
                y = int(sprite.center_y // self.tilemap.tile_height)
                if 0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height:
                    tipo =  sprite.properties.get("tipo", "?")
                    if tipo == "ostacoli":
                        grid[y][x] = 1
                    elif tipo == "danni":
                        grid[y][x] = 2
                    elif tipo == "monete":
                        grid[y][x] = 3
                    elif tipo == "cuori":
                        grid[y][x] = 4


        return grid

    def _create_buttons(self):
        button_height = 60
        button_width = 350
        button_spacing = 30
        buttons_data = [
            ("Torna al menu ", lambda:  self._go_menu()),
            ("Come giocare ", lambda: print("aa")),
            ("Impostazioni ", lambda: self.window.show_view(ImpostazioniScreen(self.view))),
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
            callback=lambda: self.retry,
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

        self.finish_buttons_win.append(RoundedButton(
            text="Nuova partita",
            center_x=self.camera.position[0] - 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback=self.go_to_mappe,
            bold=True
        ))

        self.finish_buttons_win.append(RoundedButton(
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
            callback=lambda: self._go_menu(),
            bold=True
        ))

    def go_to_mappe(self):
        from schermate.MappeScreen import MappeScreen
        self.window.show_view(MappeScreen(False))

    def _aggiorna_posizione_pulsanti(self):
        start_y = self.window.height - 540

        for i, button in enumerate(self.paused_buttons):
            button.center_x = self.camera.position[0]
            button.center_y = start_y + i * (button.height + 30)

        self.finish_buttons_gameover[0].center_x = self.camera.position[0] - 200
        self.finish_buttons_gameover[1].center_x = self.camera.position[0] + 200


        self.finish_buttons_gameover[0].center_y = self.camera.position[1] - 200
        self.finish_buttons_gameover[1].center_y = self.camera.position[1] - 200

        self.finish_buttons_win[0].center_x = self.camera.position[0] - 200
        self.finish_buttons_win[1].center_x = self.camera.position[0] + 200

        self.finish_buttons_win[0].center_y = self.camera.position[1] - 200
        self.finish_buttons_win[1].center_y = self.camera.position[1] - 200

    def _muovi_camera(self):
        screen_center_x = self.player.center_x - (self.window.width *0.5)
        screen_center_y = self.window.height *0.5

        if screen_center_x < 0:
            screen_center_x = 0

        map_width = self.tilemap.width * self.tilemap.tile_width
        if ImpostazioniLogica().is_fullscreen():
            map_width *=1.3
        if screen_center_x > map_width - self.window.width:
            screen_center_x = map_width - self.window.width

        if self.player.center_x > self.window.width *0.5:
            self.camera.position = (screen_center_x + self.window.width *0.5, screen_center_y)
        self._aggiorna_posizione_pulsanti()

    def collisioni(self):
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
            self.moneteList.append((round(moneta.center_x / self.scaling), round(moneta.center_y / self.scaling)))
            moneta.remove_from_sprite_lists()
            self.player.coins += 1
            if ImpostazioniLogica().is_audio():
                sound = arcade.Sound("Media/Sounds/coin_sound.mp3")
                sound.play(volume=0.5)
            self.tile_grid = self._build_tile_grid()
            print(f"Moneta raccolta! Monete totali: {self.player.coins}")

        for cuore in oggetti_colpiti["cuori"]:
            self.cuoriList.append((round(cuore.center_x / self.scaling), round(cuore.center_y / self.scaling)))
            cuore.remove_from_sprite_lists()
            self.player.add_health(1)
            self.tile_grid = self._build_tile_grid()
            print(f"Vita raccolta! Vita attuale: {self.player.health}")

        if oggetti_colpiti["danni"]:
            self.player.rem_health(1)
            if self.player.health <= 0:
                self.finish = "Gameover"

        map_width = self.tilemap.width * self.tilemap.tile_width
        if ImpostazioniLogica().is_fullscreen():
            map_width *= 1.3
        if self.player.center_x > map_width - 48:
            self.finish = "Win"

    def pausa(self):
        if self.finish == "Gameover":
            pass
        elif self.start_pause == 0:
            self.playerposition_x = round(self.player.center_x / self.scaling)
            self.playerposition_y = round(self.player.center_y / self.scaling)
            self.start_pause = time.time()
        else:
            self.start_time += int(time.time() - self.start_pause)
            self.start_pause = 0

    def _go_menu(self):
        from schermate.MenuScreen import MenuScreen
        self.camera.position =(self.window.width *0.5, self.window.height *0.5)
        self.camera.use()
        self.window.show_view(MenuScreen(True))

    def retry(self):
        from schermate.GiocoScreen import GiocoScreen
        self.window.show_view(GiocoScreen(self.mappa))



