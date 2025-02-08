

import arcade
import cProfile

from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.AiScreen import GiocoScreen

def main():
    larghezza_schermo = 1184
    altezza_schermo = 768
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube", visible=True)
    ImpostazioniLogica().audio_var = False
    game_view = GiocoScreen("intro.tmx", training_mode=True)
    window.show_view(game_view)
    window.set_update_rate(1 / 500)
    arcade.run()

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    profiler.dump_stats('risultati.prof')
