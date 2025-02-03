import arcade
from pygame.display import is_fullscreen

from Persistenza.ImpostazioniJSON import load_settings, save_settings
from Logica.ImpostazioniLogica import ImpostazioniLogica
class ImpostazioniScreen(arcade.View):

    def __init__(self, callback=None):
        super().__init__()
        # Posizione dei checkbox
        self.callback = callback
        self.fullscreen_checkbox_pos = (self.window.width *0.5 + 80, self.window.height *0.5 + 20)
        self.audio_checkbox_pos = (self.window.width *0.5 + 80, self.window.height *0.5 - 20)
        self.settings = ImpostazioniLogica()
        self.update_checkbox_positions()  # Calcola le posizioni iniziali

    def update_checkbox_positions(self):
        """Aggiorna le posizioni dei checkbox in base alla dimensione della finestra."""
        self.fullscreen_checkbox_pos = (self.window.width *0.5 + 80, self.window.height *0.5 + 20)
        self.audio_checkbox_pos = (self.window.width *0.5 + 80, self.window.height *0.5 - 20)

    def on_resize(self, width, height):

        """Aggiornare la posizione degli elementi quando la finestra cambia dimensione."""
        self.update_checkbox_positions()
        self.setup()

    def on_update(self, delta_time):
        pass

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)
        self.setup()

    def setup(self):
        self.camera = arcade.camera.Camera2D()


    def on_draw(self):
        self.clear()
        self.camera.use()
        arcade.draw_text("Impostazioni", self.window.width *0.5, self.window.height - 50, arcade.color.WHITE,font_size=30, anchor_x="center")
        # Draw checkbox labels and state
        fullscreen_text = "Fullscreen"
        audio_text = "Audio"

        # Draw the checkboxes
        arcade.draw_text(fullscreen_text, self.window.width *0.5 - 100, self.window.height *0.5 + 20, arcade.color.WHITE,20, anchor_x="center")
        arcade.draw_text(audio_text, self.window.width *0.5 - 100, self.window.height *0.5 - 20, arcade.color.WHITE, 20,anchor_x="center")

        self.update_checkbox_positions()
        # Draw checkbox states (checked/unchecked)
        fullscreen_checkbox = "✓" if self.settings.is_fullscreen() else "✗"
        audio_checkbox = "✓" if self.settings.is_audio() else "✗"

        arcade.draw_text(fullscreen_checkbox, self.fullscreen_checkbox_pos[0], self.fullscreen_checkbox_pos[1],arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text(audio_checkbox, self.audio_checkbox_pos[0], self.audio_checkbox_pos[1], arcade.color.WHITE,20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        # Check if fullscreen checkbox was clicked
        if self.is_checkbox_clicked(x, y, self.fullscreen_checkbox_pos):
            self.settings.set_fullscreen(self.window)
        # Check if audio checkbox was clicked
        if self.is_checkbox_clicked(x, y, self.audio_checkbox_pos):
            self.settings.set_audio()

    def is_checkbox_clicked(self, x, y, checkbox_pos):
        # Check if the mouse click is within the bounding box of the checkbox
        checkbox_x, checkbox_y = checkbox_pos
        return (checkbox_x - 20 < x < checkbox_x + 20) and (checkbox_y - 10 < y < checkbox_y + 10)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.callback is None:
                from schermate.MenuScreen import MenuScreen
                self.window.show_view(MenuScreen())
            else:
                self.callback()