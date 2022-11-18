from arcade import View, Camera

from src.worldmap import Map
from src.player.player import PlayerCharacter


# TODO: Write actual primary game view


class PrimaryGameView(View):

    def __init__(self):
        super().__init__()
        # TODO: remove placeholder variables with proper initialization

        self._placeholder_player = PlayerCharacter()

        self._placeholder_camera = Camera()

        Map.initialise()

    def on_show_view(self):
        if not Map.current:
            # Map.set_room(Map['Test', 'platforming'])
            Map.set_room(Map['JungleEdge', 'entrance'])

        self._placeholder_camera.viewport = (0, 0, self.window.width, self.window.height)
        self._placeholder_camera.projection = (0, self.window.width, 0, self.window.height)

        self._placeholder_camera.use()
        # self._placeholder_camera.zoom = 0.5

    def on_update(self, delta_time: float):
        self._placeholder_player.update()

        _target_pos = [self._placeholder_player.p_data.x - self.window.width // 2,
                       self._placeholder_player.p_data.y - self.window.height // 2]
        # _target_pos[0] = max(min(_target_pos[0], Map.current.px_width - self.window.width), 0.0)
        # _target_pos[1] = max(min(_target_pos[1], Map.current.px_height - self.window.height), 0.0)

        self._placeholder_camera.move_to(tuple(_target_pos),
                                         0.05)
        self._placeholder_camera.update()

    def on_draw(self):
        self._placeholder_camera.use()
        self.clear()
        Map.draw()
        self._placeholder_player.draw()
