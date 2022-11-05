from arcade import Window

from src.clock import Clock
from src.input import Input

from src.views.splash_view import SplashView
from src.views.primary_game_view import PrimaryGameView

from src.util import DEBUG
from data.arcade_keys_str_id import Mouse


class EngineWindow(Window):

    def __init__(self):
        super().__init__(title="Game Off 2022: God Feed", update_rate=1 / 120)
        self.game_view = PrimaryGameView()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(Mouse.key_id[button])

    def on_key_press(self, symbol: int, modifiers: int):
        self.close()

    def show_game_view(self):
        self.show_view(self.game_view)

    def on_update(self, delta_time: float):
        if not Clock.frame:
            self.show_view(SplashView())
        Clock.tick(delta_time)

        # TODO: remove all debug code
        if DEBUG:
            while Clock.frame < 1024:
                Clock.tick(delta_time)

    def on_draw(self):
        pass
