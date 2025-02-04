import arcade
import time

TILE_WIDTH = 50
TILE_HEIGHT = 50

class AnimatedPlayer(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = TILE_WIDTH
        self.height = TILE_HEIGHT
        self.texture = arcade.Texture("pietro.png", (0, 0, TILE_WIDTH, TILE_HEIGHT))  # Carica la texture (primo frame)
        self.frame_duration = 0.15  # Durata di ogni frame in secondi
        self.current_frame_time = 0  # Tempo trascorso per il frame corrente
        self.current_frame = 0  # Indice del frame
        self.total_frames = 2  # Numero totale di frame dell'animazione

    def update(self):
        # Incrementa il tempo trascorso
        self.current_frame_time += arcade.get_time_delta()

        # Se il tempo per il frame corrente è scaduto, passa al prossimo frame
        if self.current_frame_time >= self.frame_duration:
            self.current_frame_time = 0
            self.current_frame = (self.current_frame + 1) % self.total_frames  # Cicla tra i frame
            self.update_texture()

    def update_texture(self):
        # Imposta la texture da visualizzare in base al frame corrente
        # Calcola la posizione del frame da usare
        texture_x = self.current_frame * TILE_WIDTH
        self.texture = arcade.Texture("pietro.png", (texture_x, 0, TILE_WIDTH, TILE_HEIGHT))

    def draw(self):
        # Disegna lo sprite con la texture aggiornata
        self.texture.draw(self.center_x, self.center_y)

# Esegui il codice di Arcade per vedere il risultato
def main():
    arcade.open_window(800, 600, "Animazione con Tileset TSX")
    arcade.set_background_color(arcade.color.WHITE)

    animated_player = AnimatedPlayer(400, 300)
    arcade.schedule(animated_player.update, 1/60)  # Aggiorna ogni frame

    while True:
        arcade.start_render()
        animated_player.draw()
        arcade.finish_render()
        arcade.run()

if __name__ == "__main__":
    main()
