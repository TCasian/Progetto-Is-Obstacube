from audioop import reverse
import arcade
import time

from selenium.webdriver.common.devtools.v85.debugger import pause

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
        self.health = 3
        self.coins = 100
        self.immune = False
        self.last_danno = 0

    def add_health(self, val):
        temp = self.health + val
        if not temp > self.max_life:
            self.health = temp

    def rem_health(self, val):
        temp = self.health - val
        if not temp < 0 and not self.immune:
            self.health = temp

    def draw(self):
        self.left = self.center_x - self.width // 2
        self.right = self.center_x + self.width // 2
        self.bottom = self.center_y - self.height // 2
        self.top = self.center_y + self.height // 2
        color = arcade.color.RED if self.immune else self.color
        arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, color)

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def get_surrounding_grid(self, tile_grid, grid_size=10):
        # Trova la posizione del giocatore nella griglia
        player_x = int(self.center_x // TILE_WIDTH)
        player_y = int(self.center_y // TILE_HEIGHT)

        # Calcola quante celle della griglia sono coperte dal giocatore
        player_width_tiles = int(self.width // TILE_WIDTH)
        player_height_tiles = int(self.height // TILE_HEIGHT)

        # Definisci i limiti della griglia
        half_grid = grid_size // 2
        start_x = max(0, player_x - half_grid)  # Inizia a metà griglia a sinistra del giocatore
        end_x = min(len(tile_grid[0]) - 1, player_x + half_grid)  # Termina a metà griglia a destra del giocatore
        start_y = max(0, player_y - half_grid)  # Inizia a metà griglia sotto il giocatore
        end_y = min(len(tile_grid) - 1, player_y + half_grid)  # Termina a metà griglia sopra il giocatore

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
        self.tilemap = arcade.load_tilemap("Media/mappe/mappa_test.tmx", scaling=TILE_SCALING)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.ostacoli = self.scene["ostacoli"] if "ostacoli" in self.scene else arcade.SpriteList()
        self.bombe = self.scene["bombe"] if "bombe" in self.scene else arcade.Sprite()
        self.monete = self.scene["monete"] if "monete" in self.scene else arcade.SpriteList()
        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()
        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()

        self.monete.rescale(1.3)
        self.player = Player(100, 100)
        self.start_time = time.time()
        self.camera = arcade.camera.Camera2D()
        self.tile_grid = self._build_tile_grid()
        self.paused = False

    def _build_tile_grid(self):
        """
        Costruisce una griglia di tile basata sulla mappa.
        Ogni cella della griglia contiene il tipo di tile (o "[]" se è vuoto).
        """
        tile_width = self.tilemap.tile_width
        tile_height = self.tilemap.tile_height
        map_width = self.tilemap.width
        map_height = self.tilemap.height

        # Inizializza una griglia vuota
        grid = [["[]" for _ in range(map_width)] for _ in range(map_height)]

        # Popola la griglia con i tile degli ostacoli
        for sprite in self.ostacoli:
            x = int(sprite.center_x // tile_width)
            y = int(sprite.center_y // tile_height)
            if 0 <= x < map_width and 0 <= y < map_height:
                grid[y][x] = sprite.properties.get("tipo", "Unknown")

        for sprite in self.monete:
            x = int(sprite.center_x // tile_width)
            y = int(sprite.center_y // tile_height)
            if 0 <= x < map_width and 0 <= y < map_height:
                grid[y][x] = sprite.properties.get("tipo", "Unknown")
        return grid

    def on_show(self):
        arcade.set_background_color(arcade.color.GOLD)

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.scene.draw()
        self.player.draw()

        self._draw_info()

    def on_update(self, delta_time):
        if not self.paused:
            self.player.update()
            if arcade.check_for_collision_with_list(self.player, self.ostacoli):
                self.player.center_x -= self.player.change_x
                self.player.center_y -= self.player.change_y

            monete_colpite = arcade.check_for_collision_with_list(self.player, self.monete)
            for moneta in monete_colpite:
                moneta.remove_from_sprite_lists()
                self.player.coins += 1
                print(f"Moneta raccolta! Monete totali: {self.player.coins}")
            print(delta_time)

            cuori_colpiti = arcade.check_for_collision_with_list(self.player, self.cuori)
            for cuori in cuori_colpiti:
                cuori.remove_from_sprite_lists()
                self.player.add_health(1)
                print(f"vita raccolta {self.player.health}")


            danni_colpiti = arcade.check_for_collision_with_list(self.player, self.danni)
            for danni in danni_colpiti:
                if time.time() - self.player.last_danno >= 0.5:
                    self.player.add_health(-1)
                    self.player.last_danno = time.time()
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
            self.paused = not self.paused
        elif key == arcade.key.SPACE:
            self.print_player_grid()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0
        elif key in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0

    def _muovi_camera(self):
        screen_center_x = self.player.center_x - (self.window.width / 2)
        screen_center_y = self.window.height / 2

        if screen_center_x < 0:
            screen_center_x = 0

        map_width = self.tilemap.width * self.tilemap.tile_width
        if screen_center_x > map_width - self.window.width:
            screen_center_x = map_width - self.window.width

        if self.player.center_x > self.window.width // 2:
            self.camera.position = (screen_center_x + self.window.width / 2, screen_center_y)

    def _draw_info(self):
        tempo_width, tempo_height = 300, 120
        cuori_width, cuori_height = 250, 70
        soldi_width, soldi_height = 250, 70
        pausa_width, pausa_height = 800 - 8, 500

        y_offset = self.window.height - 30

         #spostare in draw_paused
        if self.paused:
            pausa_x = self.camera.position[0]
            pausa_y = y_offset - pausa_height + tempo_height
            tempo = RectangleBorder(
                pausa_x,
                pausa_y,
                pausa_width,
                pausa_height,
                bg_color=(217, 147, 8),
            )
            tempo.draw()

        cuori_x = self.camera.position[0] - tempo_width // 2 - cuori_width // 2 + 5
        cuori_y = y_offset - cuori_height // 2 - 25
        cuori = RectangleBorder(
            cuori_x,
            cuori_y,
            cuori_width,
            cuori_height,
            bg_color=(217, 147, 8),
        )
        cuori.draw()

        cuore_pieno_sprite = arcade.Sprite("Media/img/cuore_pieno.png", scale=1.3)
        cuore_vuoto_sprite = arcade.Sprite("Media/img/cuore_vuoto.png", scale=1.3)
        spacing = 1
        start_x = cuori_x - cuori_width // 2 + 35

        for i in range(self.player.max_life):
            if i < self.player.health:
                cuore_pieno_sprite.center_x = start_x + i * (
                            cuore_pieno_sprite.width + spacing)
                cuore_pieno_sprite.center_y = cuori_y + (
                            cuori_height - cuore_pieno_sprite.height) // 2 - 10
                arcade.draw_texture_rect(cuore_pieno_sprite.texture, cuore_pieno_sprite.rect)
            else:
                cuore_vuoto_sprite.center_x = start_x + i * (
                            cuore_vuoto_sprite.width + spacing)
                cuore_vuoto_sprite.center_y = cuori_y + (
                            cuori_height - cuore_vuoto_sprite.height) // 2 - 10
                arcade.draw_texture_rect(cuore_vuoto_sprite.texture, cuore_vuoto_sprite.rect)

        soldi_x = self.camera.position[0] + tempo_width // 2 + soldi_width // 2 - 5
        soldi_y = y_offset - soldi_height // 2 - 25
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
            soldi_x - (soldi_width // 4) - 55,
            soldi_y - soldi_height // 2 + 25,
            arcade.color.WHITE,
            font_size=24,
            bold=True
        )

        moneta_sprite = arcade.Sprite("Media/img/coin.png", scale=1.2)
        moneta_sprite.center_x = soldi_x - (soldi_width // 4) + 20
        moneta_sprite.center_y = soldi_y  # Posizione Y (centrata verticalmente)
        arcade.draw_texture_rect(moneta_sprite.texture, moneta_sprite.rect)

        tempo_x = self.camera.position[0]
        tempo_y = y_offset - tempo_height // 2
        tempo = RectangleBorder(
            tempo_x,
            tempo_y,
            tempo_width,
            tempo_height,
            bg_color=(217, 147, 8),
        )
        tempo.draw()

        tempo_trascorso = int(time.time() - self.start_time)  # Tempo in secondi
        minuti = tempo_trascorso // 60
        secondi = tempo_trascorso % 60

        tempo_testo = f"{minuti:02}:{secondi:02}"
        arcade.draw_text(
            tempo_testo,
            tempo_x-75,
            tempo_y - 20,
            arcade.color.WHITE,
            font_size=50,
            bold=True
        )

    def _draw_paused(self):
        pass