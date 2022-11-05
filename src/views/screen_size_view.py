from arcade import View, get_screens, get_display_size


class ScreenSizeView(View):

    def __init__(self):
        super().__init__()
        _screen = get_screens()[0]
        self.window.set_fullscreen(True, _screen)

    def on_update(self, delta_time: float):
        self.window.show_game_view()
