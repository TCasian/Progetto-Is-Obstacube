import arcade

class SettingsScreen(arcade.View):

    def on_update(self, delta_time):
        print("settings da fare")

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Impostazioni", self.window.width / 2, self.window.height / 2, arcade.color.WHITE, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuScreen())