import arcade
import time
from Logica.ImpostazioniLogica import ImpostazioniLogica

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
        if ImpostazioniLogica().is_audio():
            sound = arcade.Sound("Media/Sounds/health_down_sound.mp3")
            sound.play(volume=0.5)
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

