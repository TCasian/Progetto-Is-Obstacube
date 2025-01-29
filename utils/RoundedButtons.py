import arcade

class RoundedButton:
    def __init__(self, text, center_x, center_y, width, height, bg_color, bg_hover, text_color, hover_text_color, text_size, bold, callback=None):
        self.text = text
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.bg_hover = bg_hover
        self.text_color = text_color
        self.hover_text_color = hover_text_color
        self.text_size = text_size
        self.callback = callback
        self.is_hovered = False
        self.bold = bold
        self.corner_radius = 10  # Raggio degli angoli arrotondati

    def draw(self):
        # Calcola le coordinate del bottone
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2

        # Scegli il colore in base allo stato hover
        current_bg_color = self.bg_hover if self.is_hovered else self.bg_color
        current_text_color = self.hover_text_color if self.is_hovered else self.text_color

        # Disegna il corpo del bottone con angoli arrotondati
        self._draw_rounded_rectangle(left, right, bottom, top, current_bg_color)

        # Disegna il bordo esterno nero
        self._draw_border(left, right, bottom, top, current_bg_color)

        # Disegna il testo centrato
        arcade.draw_text(
            self.text, self.center_x, self.center_y,
            current_text_color, font_size=self.text_size,
            anchor_x="center", anchor_y="center", bold=self.bold
        )

    def _draw_rounded_rectangle(self, left, right, bottom, top, color):
        """Disegna il corpo del bottone con angoli arrotondati"""
        # Parte centrale rettangolare
        arcade.draw_lrbt_rectangle_filled(
            left + self.corner_radius, right - self.corner_radius,
            bottom, top, color
        )
        arcade.draw_lrbt_rectangle_filled(
            left, right,
            bottom + self.corner_radius, top - self.corner_radius,
            color
        )



        # Cerchi per gli angoli arrotondati
        arcade.draw_circle_filled(
            left + self.corner_radius, bottom + self.corner_radius,
            self.corner_radius, color
        )
        arcade.draw_circle_filled(
            left + self.corner_radius, top - self.corner_radius,
            self.corner_radius, color
        )
        arcade.draw_circle_filled(
            right - self.corner_radius, bottom + self.corner_radius,
            self.corner_radius, color
        )
        arcade.draw_circle_filled(
            right - self.corner_radius, top - self.corner_radius,
            self.corner_radius, color
        )

    def _draw_border(self, left, right, bottom, top, color):
        """Disegna solo il bordo esterno nero"""
        # Parte centrale rettangolare del bordo
        arcade.draw_lrbt_rectangle_outline(
            left + self.corner_radius, right - self.corner_radius,
            bottom, top, arcade.color.BLACK, 2
        )
        arcade.draw_lrbt_rectangle_outline(
            left, right,
            bottom + self.corner_radius, top - self.corner_radius,
            arcade.color.BLACK, 2
        )
        arcade.draw_lrbt_rectangle_filled(
            left - 1 + self.corner_radius, right + 1 - self.corner_radius,
            bottom + 1, top - 1, color
        )
        arcade.draw_lrbt_rectangle_filled(
            left + 1, right - 1,
            bottom - 1 + self.corner_radius, top + 1 - self.corner_radius,
            color
        )


        # Archi per gli angoli arrotondati del bordo
        arcade.draw_arc_outline(
            left + self.corner_radius, bottom + self.corner_radius,
            self.corner_radius * 2, self.corner_radius * 2,
            arcade.color.BLACK, 180, 270, 3
        )
        arcade.draw_arc_outline(
            left + self.corner_radius, top - self.corner_radius,
            self.corner_radius * 2, self.corner_radius * 2,
            arcade.color.BLACK, 90, 180, 3
        )
        arcade.draw_arc_outline(
            right - self.corner_radius, bottom + self.corner_radius,
            self.corner_radius * 2, self.corner_radius * 2,
            arcade.color.BLACK, 270, 360, 3
        )
        arcade.draw_arc_outline(
            right - self.corner_radius, top - self.corner_radius,
            self.corner_radius * 2, self.corner_radius * 2,
            arcade.color.BLACK, 0, 90, 3
        )

    def check_collision(self, x, y):
        """Controlla se il punto (x, y) è dentro il bottone"""
        return (
            self.center_x - self.width / 2 <= x <= self.center_x + self.width / 2
            and self.center_y - self.height / 2 <= y <= self.center_y + self.height / 2
        )

    def on_click(self, x, y):
        """Chiama la funzione callback se viene premuto il pulsante"""
        if self.check_collision(x, y) and self.callback:
            self.callback()

    def on_hover(self, x, y):
        """Cambia lo stato hover se il cursore è sopra il bottone"""
        self.is_hovered = self.check_collision(x, y)