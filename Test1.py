import time
import arcade
from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.GiocoScreen import GiocoScreen
from schermate.ImpostazioniScreen import ImpostazioniScreen
from schermate.MenuScreen import MenuScreen

def test_avvio_gioco():
    larghezza_schermo = 1184
    altezza_schermo = 768
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube",fullscreen=False, visible=False)
    # TC_1.1.1-2
    assert window.fullscreen is False, \
        "L'interfaccia non è avviata correttamente"
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube", fullscreen=True, visible=False)
    assert window.fullscreen is True, \
        "L'interfaccia non è avviata correttamente"
    window.set_update_rate(1 / 60)
    arcade.exit()

def test_intro_load():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = MenuScreen(False)
    window.show_view(intro_view)
    assert isinstance(window.current_view, MenuScreen), "L'intro non è stata caricata correttamente"
    arcade.close_window()

def test_exit():
    """Testa il caricamento del menu e la chiusura tramite il pulsante 'Esci'."""
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = MenuScreen(False)
    # Simula il click sul pulsante "Esci"
    exit_button = intro_view.get_exit_button()  # Supponendo che ci sia un metodo per ottenere il pulsante
    assert exit_button is not None, "Il pulsante 'Esci' non è stato trovato"

    exit_button.on_click(exit_button.center_x, exit_button.center_y)  # Simula la pressione del pulsante
    try:
        arcade.get_window()
    except RuntimeError:
        closed_properly = True
    else:
        closed_properly = False

    assert closed_properly, "Il gioco non si è chiuso correttamente"
    arcade.close_window()

def test_fullscreen_setting():
    """Testa il caricamento del menu e la chiusura tramite il pulsante 'Esci'."""
    fullscreen = ImpostazioniLogica().is_fullscreen()
    window = arcade.Window(1184, 768, "Obstacube", fullscreen, visible=False)
    intro_view = ImpostazioniScreen()
    window.show_view(intro_view)
    x, y = intro_view.fullscreen_checkbox_pos
    intro_view.on_mouse_press(x, y, intro_view.fullscreen_checkbox_pos, 0)
    assert window.fullscreen is not fullscreen
    arcade.close_window()

def test_audio_setting():
    """Testa il caricamento del menu e la chiusura tramite il pulsante 'Esci'."""
    audio = ImpostazioniLogica().is_audio()
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = ImpostazioniScreen()
    x, y = intro_view.audio_checkbox_pos
    intro_view.on_mouse_press(x, y, intro_view.audio_checkbox_pos, 0)
    assert ImpostazioniLogica().is_audio() is not audio
    arcade.close_window()

def test_partita_avviata():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    assert intro_view.gioco.tilemap is not None
    assert intro_view.gioco.player.health ==  intro_view.gioco.player.max_life
    assert intro_view.gioco.player.coins == 0
    assert intro_view.gioco.start_time < time.time()+1
    arcade.close_window()


