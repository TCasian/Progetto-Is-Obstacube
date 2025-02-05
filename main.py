import arcade

from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.MenuScreen import MenuScreen


def main():
    larghezza_schermo = 1184
    altezza_schermo = 768
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube", fullscreen=ImpostazioniLogica().is_fullscreen())
    window.show_view(MenuScreen(False))
    window.set_update_rate(1 / 60)
    arcade.run()

if __name__ == '__main__':
    main()