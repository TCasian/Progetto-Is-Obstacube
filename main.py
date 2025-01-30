import arcade

from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.MenuScreen import MenuScreen


def main():
    larghezza_schermo = 1184
    altezza_schermo = 768
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube")
    window.set_fullscreen(ImpostazioniLogica().fullscreen_var)
    menu_view = MenuScreen()
    window.show_view(menu_view)
    window.set_update_rate(1 / 60)
    arcade.run()

if __name__ == '__main__':
    main()