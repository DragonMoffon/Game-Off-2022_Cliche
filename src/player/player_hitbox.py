from typing import Tuple

from arcade import Sprite, SpriteList, SpriteSolidColor

from src.player.player_data import PlayerData

from src.util import dist, lerp, round_point


class PlayerHitbox:

    def __init__(self, _source: Sprite, _position: PlayerData):
        self._source = _source
        self._position = _position

        self._horizontal_sensor = SpriteSolidColor(int(self._position.right - self._position.left), 1, (0, 255, 0))
        self._vertical_sensor = SpriteSolidColor(1, int(self._position.top - self._position.bottom), (255, 0, 0))
        self._ledge_sensor = SpriteSolidColor(8, 8, (0, 0, 255))

    def _resolve_collision(self, _old_check: Tuple[float, float], _new_check: Tuple[float, float],
                           _sensor: Sprite, _collision_layer: SpriteList):
        _length = int(dist(_old_check, _new_check) // 32) + 1

        for step in range(_length + 1):
            t = step / _length
            _pos = lerp(_old_check[0], _new_check[0], t), lerp(_old_check[1], _new_check[1], t)
            _sensor.position = round_point(_pos)
            _collisions = _sensor.collides_with_list(_collision_layer)
            if len(_collisions):
                _collisions.sort(key=lambda sprite: sprite.center_y, reverse=True)
                return True, _collisions[0]
        return False, None

    def hit_ground(self, _collision_layer: SpriteList) -> Tuple[bool, Sprite]:
        _old_check = round_point((self._position.old_x, self._position.old_bottom-1))
        _new_check = round_point((self._position.x, self._position.bottom-1))
        _hit, _collision = self._resolve_collision(_old_check, _new_check, self._horizontal_sensor, _collision_layer)
        return _hit, _collision

    def hit_ciel(self, _collision_layer: SpriteList) -> Tuple[bool, Sprite]:
        _old_check = round_point((self._position.old_x, self._position.old_top+1))
        _new_check = round_point((self._position.x, self._position.top+1))
        _hit, _collision = self._resolve_collision(_old_check, _new_check, self._horizontal_sensor, _collision_layer)
        return _hit, _collision

    def hit_left(self, _collision_layer: SpriteList) -> Tuple[bool, Sprite]:
        _old_check = round_point((self._position.old_left-1, self._position.old_y))
        _new_check = round_point((self._position.left-1, self._position.y))
        _hit, _collision = self._resolve_collision(_old_check, _new_check, self._vertical_sensor, _collision_layer)

        return _hit, _collision

    def hit_right(self, _collision_layer: SpriteList) -> Tuple[bool, Sprite]:
        _old_check = round_point((self._position.old_right+1, self._position.old_y))
        _new_check = round_point((self._position.right+1, self._position.y))
        _hit, _collision = self._resolve_collision(_old_check, _new_check, self._vertical_sensor, _collision_layer)
        return _hit, _collision

    def check_ledge_vertical_left(self, _collision_layer: SpriteList):
        _old_check = round_point((self._position.old_left - 9.0, self._position.old_top + 9.0))
        _new_check = round_point((self._position.left - 9.0, self._position.top + 9.0))
        _ledge_hit, _ledge_collision = self._resolve_collision(_old_check, _new_check,
                                                               self._ledge_sensor, _collision_layer)

        return not _ledge_hit

    def check_ledge_vertical_right(self, _collision_layer: SpriteList):
        _old_check = round_point((self._position.old_right + 9.0, self._position.old_top + 9.0))
        _new_check = round_point((self._position.right + 9.0, self._position.top + 9.0))
        _ledge_hit, _ledge_collision = self._resolve_collision(_old_check, _new_check,
                                                               self._ledge_sensor, _collision_layer)

        return not _ledge_hit

    def check_ledge_horizontal_left(self, _collision_layer: SpriteList):
        _old_check = round_point((self._position.old_left - 9.0, self._position.old_bottom - 9.0))
        _new_check = round_point((self._position.left - 9.0, self._position.old_bottom - 9.0))
        _ledge_hit, _ledge_collision = self._resolve_collision(_old_check, _new_check,
                                                               self._ledge_sensor, _collision_layer)

    def check_ledge_horizontal_right(self, _collision_layer: SpriteList):
        _old_check = round_point((self._position.old_right + 9.0, self._position.old_bottom - 9.0))
        _new_check = round_point((self._position.right + 9.0, self._position.bottom - 9.0))

    def debug_draw(self):
        self._horizontal_sensor.position = self._position.old_x, self._position.old_bottom-1
        self._horizontal_sensor.draw(pixelated=True)
        self._horizontal_sensor.center_y = self._position.old_top+1
        self._horizontal_sensor.draw(pixelated=True)

        self._vertical_sensor.position = self._position.old_left-1, self._position.old_y
        self._vertical_sensor.draw(pixelated=True)
        self._vertical_sensor.center_x = self._position.old_right+1
        self._vertical_sensor.draw(pixelated=True)

        self._horizontal_sensor.position = self._position.x, self._position.bottom-1
        self._horizontal_sensor.draw(pixelated=True)
        self._horizontal_sensor.center_y = self._position.top+1
        self._horizontal_sensor.draw(pixelated=True)

        self._vertical_sensor.position = self._position.left-1, self._position.y
        self._vertical_sensor.draw(pixelated=True)
        self._vertical_sensor.center_x = self._position.right+1
        self._vertical_sensor.draw(pixelated=True)

        half_width = (self._position.x-self._position.left)
        self._ledge_sensor.position = (self._position.x + (half_width + 9) * self._position.direction,
                                       self._position.top + 9)
        self._ledge_sensor.draw(pixelated=True)
        self._ledge_sensor.position = (self._position.old_x + (half_width + 9) * self._position.direction,
                                       self._position.top + 9)
        self._ledge_sensor.draw(pixelated=True)

        self._ledge_sensor.position = (self._position.x + (half_width + 9) * self._position.direction,
                                       self._position.bottom - 9)
        self._ledge_sensor.draw(pixelated=True)
