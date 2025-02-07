import arcade

from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.AiScreen import GiocoScreen
if __name__ == "__main__":
    larghezza_schermo = 1184
    altezza_schermo = 768
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube", visible=True)
    ImpostazioniLogica().audio_var = False
    game_view = GiocoScreen("foresta.tmx",training_mode=True)
    window.show_view(game_view)
    arcade.run()