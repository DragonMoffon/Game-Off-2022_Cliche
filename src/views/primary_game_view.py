import arcade
from arcade import View, draw_lrtb_rectangle_filled

from src.clock import Clock


class PrimaryGameView(View):

    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        draw_lrtb_rectangle_filled(0, self.window.width, self.window.height, 0,
                                   [255, 255, 255, min(Clock.frame-1024, 255)])
