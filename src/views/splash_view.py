from math import sin, pi

from arcade import View, Sprite, load_texture

from src.clock import Clock
from src.views.screen_size_view import ScreenSizeView


class SplashView(View):

    def __init__(self):
        super().__init__()
        self._splash_sprite = Sprite(":assets:/textures/arcade-logo-splash.png",
                                     center_x=self.window.width // 2, center_y=self.window.height // 2)
        self._splash_sprite.alpha = 0

    def on_update(self, delta_time: float):
        if Clock.frame - 512 < 512:
            self._splash_sprite.alpha = sin(pi * (Clock.frame) / 512)**2 * 255
        else:
            self.window.show_view(ScreenSizeView())
        if Clock.frame == 512:
            self._splash_sprite.texture = load_texture(":assets:/textures/dragon-bakery-splash.png")

    def on_draw(self):
        self.clear()
        if Clock.frame - 512 < 512:
            self._splash_sprite.draw()
