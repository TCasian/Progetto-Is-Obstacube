import arcade



WIDTH = 1024
HEIGHT = 767

class FadeManager:
    def __init__(self, fade_rate=0.01):
        self.opacita = None
        self.target_opacity = None
        self.color = None
        self.target_color = None  # in rgb (0, 0, 0)
        self.fade_rate = fade_rate  # velocita fade (0 a 1)
        self.progress = None  # completamento (da 0 a 1)
        self.is_fading = False


    def start_fade(self, start_color, target_color):
        """Avvia il fade tra due colori RGBA."""
        if not self.is_fading:
            self.start_color = start_color
            self.target_color = target_color
            self.color = start_color
            self.progress = 0
            self.is_fading = True

    def update(self):
        if not self.is_fading:
           # print("ritorno hihi")
            return

        self.progress += self.fade_rate
        self.progress = min(self.progress, 1)  # Non supera 1

        self.color = self._prendi_colore(self.start_color, self.target_color, self.progress)

        if self.progress >= 1:
            self.is_fading = False


    def draw(self):
        if self.color:
            arcade.draw_lrbt_rectangle_filled(
                left=0,
                right=WIDTH,
                top=HEIGHT,
                bottom=0,
                color=self.color
            )


    def _prendi_colore(self, color1, color2, t):
        return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(4))