import arcade
import time
import xml.etree.ElementTree as ET
from Logica.ImpostazioniLogica import ImpostazioniLogica
from Persistenza.PlayerJSON import load_player, save_player

TILE_SCALING = 1.0
PLAYER_SPEED = 5
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32


class Player(arcade.Sprite):

    def __init__(self, x, y,):
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

        self.frames = []
        self.frame_durations = []
        self.current_frame = 0
        self.time_since_last_frame = 0

        self.load_frames_from_tsx(f"Media/Skins/{load_player()["corrente"]}.tsx")

    def load_frames_from_tsx(self, tsx_path):
        tree = ET.parse(tsx_path)
        root = tree.getroot()

        image_source = root.find("image").attrib["source"]
        image = arcade.load_texture("Media/Skins/"+image_source)

        tile_width = int(root.attrib["tilewidth"])
        tile_height = int(root.attrib["tileheight"])
        columns = int(root.attrib["columns"])

        animation_frames = root.find("tile/animation")
        for frame in animation_frames.findall("frame"):
            tile_id = int(frame.attrib["tileid"])
            duration = int(frame.attrib["duration"]) / 1000  # da ms a secondi

            col = tile_id % columns
            row = tile_id // columns

            cropped_texture = image.crop(
                col * tile_width, row * tile_height,
                tile_width, tile_height
            )
            self.frames.append(cropped_texture)
            self.frame_durations.append(duration)

    def draw(self):
        immune = (time.time() - self.last_danno <= 0.3)
        color = arcade.color.RED if immune else self.color

        self.left = self.center_x - self.width * 0.5
        self.right = self.center_x + self.width * 0.5
        self.bottom = self.center_y - self.height * 0.5
        self.top = self.center_y + self.height * 0.5

        rect = arcade.Rect(self.left, self.right, self.top, self.bottom, self.width, self.height, self.center_x,
                           self.center_y)
        arcade.draw_texture_rect(self.frames[self.current_frame], rect, color=color)

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        self.time_since_last_frame += 0.01
        if self.time_since_last_frame >= self.frame_durations[self.current_frame]:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.time_since_last_frame = 0

    def add_health(self, val):
        if ImpostazioniLogica().is_audio():
            sound = arcade.Sound("Media/Sounds/health_up_sound.wav")
            sound.play(volume=0.5)
        temp = self.health + val
        if not temp > self.max_life:
            self.health = temp

    def rem_health(self, val):
        if ImpostazioniLogica().is_audio() and time.time() - self.last_danno >= 0.3:
            sound = arcade.Sound("Media/Sounds/health_down_sound.mp3")
            sound.play(volume=0.5)
        temp = self.health - val
        if not temp < 0 and time.time() - self.last_danno >= 0.3:
            self.health = temp
            self.last_danno = time.time()

    def get_surrounding_grid(self, tile_grid, grid_size=10):
        player_x = int(self.center_x // TILE_WIDTH)
        player_y = int(self.center_y // TILE_HEIGHT)

        player_width_tiles = int(self.width // TILE_WIDTH)
        player_height_tiles = int(self.height // TILE_HEIGHT)

        half_grid = int(grid_size * 0.5)
        start_x = max(0, player_x - half_grid)
        end_x = min(len(tile_grid[0]) - 1, player_x + half_grid)
        start_y = max(0, player_y - half_grid)
        end_y = min(len(tile_grid) - 1, player_y + half_grid)

        grid = []
        for y in range(start_y, end_y + 1):
            row = []
            for x in range(start_x, end_x + 1):
                if (player_x <= x < player_x + player_width_tiles and
                        player_y <= y < player_y + player_height_tiles):
                    row.append("PLAYER")
                else:
                    row.append(tile_grid[y][x])
            grid.append(row)

        return grid

    def salva_stat(self):
       a = load_player()
       print(a["monete"])
       save_player(a["monete"]+self.coins, a["corrente"])