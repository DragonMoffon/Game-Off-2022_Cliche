from arcade import Window

from src.clock import Clock
from src.input import Input, Button

from src.views.splash_view import SplashView
from src.views.primary_game_view import PrimaryGameView

from src.util import DEBUG


class EngineWindow(Window):

    def __init__(self):
        super().__init__(title="Game Off 2022: God Feed", update_rate=1 / 120)
        self._background_color = (255, 255, 255)
        self.game_view = PrimaryGameView()
        Input.get_button("ESCAPE").register_press_observer(self.call_close)

        self._spike_count = 0

    def call_close(self, button: Button):
        self.close()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        Input.p_mouse_press(button)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        Input.p_mouse_release(button)

    def on_key_press(self, symbol: int, modifiers: int):
        Input.p_key_press(symbol)

    def on_key_release(self, symbol: int, modifiers: int):
        Input.p_key_release(symbol)

    def show_game_view(self):
        self.show_view(self.game_view)

    def on_update(self, delta_time: float):
        if not Clock.frame:
            self.show_view(SplashView())

        Clock.tick(delta_time)
        Input.p_key_held()

        # TODO: remove all debug code
        if DEBUG:
            while Clock.frame < 1024:
                Clock.tick(delta_time)


    def on_draw(self):
        pass
