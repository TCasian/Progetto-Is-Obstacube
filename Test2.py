import time
import arcade
from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.GiocoScreen import GiocoScreen
from schermate.ImpostazioniScreen import ImpostazioniScreen
from schermate.MenuScreen import MenuScreen

def test_movimento_player():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    start_x, start_y = intro_view.gioco.player.center_x, intro_view.gioco.player.center_y
    intro_view.on_key_press(arcade.key.W, 0)
    intro_view.gioco.player.update()
    intro_view.on_key_release(arcade.key.W, None)
    assert intro_view.gioco.player.center_y > start_y
    intro_view.gioco.player.center_x, intro_view.gioco.player.center_y = start_x, start_y
    intro_view.on_key_press(arcade.key.D, 0)
    intro_view.gioco.player.update()
    intro_view.on_key_release(arcade.key.D, None)
    assert intro_view.gioco.player.center_x > start_x
    intro_view.gioco.player.center_x, intro_view.gioco.player.center_y = start_x, start_y
    intro_view.on_key_press(arcade.key.S, 0)
    intro_view.gioco.player.update()
    intro_view.on_key_release(arcade.key.S, None)
    assert intro_view.gioco.player.center_y < start_y
    intro_view.gioco.player.center_x, intro_view.gioco.player.center_y = start_x, start_y
    intro_view.on_key_press(arcade.key.A, 0)
    intro_view.gioco.player.update()
    intro_view.on_key_release(arcade.key.A, None)
    assert intro_view.gioco.player.center_x < start_x
    arcade.close_window()

def test_collisione_con_ostacolo():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.gioco.player.center_x = 200
    intro_view.gioco.player.center_y = 200
    intro_view.on_key_press(arcade.key.S, 0)
    for i in range(1, 200):
        intro_view.gioco.player.update()
        intro_view.gioco.collisioni()
    assert intro_view.gioco.player.center_y == 145
    arcade.close_window()

def test_moneta_raccolta():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.gioco.player.center_x = 140
    intro_view.gioco.player.center_y = 200
    intro_view.on_key_press(arcade.key.S, 0)
    for i in range(1, 20):
        intro_view.gioco.player.update()
        intro_view.gioco.collisioni()
    assert intro_view.gioco.player.coins > 0
    arcade.close_window()

def test_danno_applicato():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.gioco.player.center_x = 270
    intro_view.gioco.player.center_y = 200
    intro_view.on_key_press(arcade.key.S, 0)
    for i in range(1, 10):
        intro_view.gioco.player.update()
        intro_view.gioco.collisioni()
    assert intro_view.gioco.player.health < intro_view.gioco.player.max_life
    arcade.close_window()

def test_cuore_raccolto():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.gioco.player.center_x = 50
    intro_view.gioco.player.center_y = 200
    intro_view.on_key_press(arcade.key.S, 0)
    intro_view.gioco.player.rem_health(1)
    for i in range(1, 15):
        intro_view.gioco.player.update()
        intro_view.gioco.collisioni()
    assert intro_view.gioco.player.health == intro_view.gioco.player.max_life
    arcade.close_window()

def test_game_over():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.gioco.player.center_x = 280
    intro_view.gioco.player.center_y = 150
    while intro_view.gioco.player.health > 0:
        intro_view.gioco.player.update()
        intro_view.gioco.collisioni()
    assert intro_view.gioco.finish == "Gameover"
    arcade.close_window()

def test_gioco_in_pausa():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.on_key_press(arcade.key.ESCAPE, 0)
    assert intro_view.gioco.start_pause > 0
    intro_view.on_key_press(arcade.key.ESCAPE, 0)
    assert intro_view.gioco.start_pause == 0
    arcade.close_window()

def test_vittoria():
    window = arcade.Window(1184, 768, "Obstacube", fullscreen=False, visible=False)
    intro_view = GiocoScreen("test_case.tmx")
    window.show_view(intro_view)
    intro_view.on_key_press(arcade.key.D, 0)
    for i in range(1, 100):
        intro_view.gioco.player.update()
        intro_view.gioco.collisioni()
    assert intro_view.gioco.finish == "Win"
    arcade.close_window()