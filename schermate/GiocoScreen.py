import arcade

class GiocoScreen(arcade.View):

    def on_update(self, delta_time):
        print("gioco da fare")

    def on_show(self):
        arcade.set_background_color(arcade.color.GOLD)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Benvenuto al gioco!", self.window.width / 2, self.window.height / 2, arcade.color.WHITE, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuScreen())