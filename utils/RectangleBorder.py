import arcade

class RectangleBorder:
    def __init__(self, center_x, center_y, width, height, bg_color, border=True, corner_radius=10):

        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.border= border
        self.corner_radius = 10  # Raggio degli angoli arrotondati

    def draw(self):
        # Calcola le coordinate del bottone
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2

        # Scegli il colore in base allo stato hover

        # Disegna il corpo del bottone con angoli arrotondati
        self._draw_rounded_rectangle(left, right, bottom, top, self.bg_color)

        # Disegna il bordo esterno nero
        self._draw_border(left, right, bottom, top, self.bg_color)



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

