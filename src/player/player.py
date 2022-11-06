from arcade import Sprite, SpriteSolidColor, tilemap

from src.input import Input, Button
from src.clock import Clock

from src.util import lerp, dist
from math import sqrt

# TODO: Complete Input Code and Physics integration


class PlayerCharacter:
    """
    PlayerCharacter holds every part of the player in the game world, and only handles input. The movement is done
    in the physics engine, and the sprite at the core draws everything.
    """

    def __init__(self, _chamber: tilemap.TileMap):
        # TODO: make actual sprite and setup animations

        self._sprite = Sprite(":assets:/textures/characters/placeholder_player.png")
        self._sprite.bottom = 128.0
        self._sprite.left = 64.0

        # TODO: remove placeholder variables
        self._horizontal_sensor = SpriteSolidColor(int(abs(self._sprite.right - self._sprite.left)-2), 1, (255, 0, 0))
        self._vertical_sensor = SpriteSolidColor(1, int(abs(self._sprite.top - self._sprite.bottom)-2), (0, 255, 0))

        self._chamber: tilemap.TileMap = _chamber

        self._player_acceleration = 15.0 * 32.0
        self._player_deceleration = 30.0 * 32.0
        self._player_turn = 60.0 * 32.0
        self._player_direction = 0.0
        self._max_velocity = 10.0 * 32.0
        self._target_velocity_x = 0.0
        self._velocity_x = 0.0
        self._velocity_y = 0.0

        self._on_ground = True

        Input.get_axis("HORIZONTAL").register_observer(self.horizontal_movement)
        Input.get_button("JUMP").register_press_observer(self.jump)

    def update(self):
        _diff = self._target_velocity_x - self._velocity_x
        _acceleration = self._player_deceleration
        if self._target_velocity_x:
            if self._velocity_x / self._target_velocity_x < 0:
                _acceleration = self._player_turn
            else:
                _acceleration = self._player_acceleration

        _acceleration = min(abs(_diff), _acceleration * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        self._velocity_x += _acceleration

        self._velocity_y -= 1024.0 * Clock.delta_time
        self._on_ground = False

        _old_position = self.center_x, self._sprite.bottom
        self._sprite.center_x += self._velocity_x * Clock.delta_time
        self._sprite.center_y += self._velocity_y * Clock.delta_time

        self._horizontal_sensor.position = (self._sprite.center_x, self._sprite.bottom)

        if self._velocity_y*Clock.delta_time <= 0.0 and _old_position != (self.center_x, self._sprite.bottom):
            _length = int(dist(_old_position, (self.center_x, self._sprite.bottom))//32)+1
            for step in range(_length+1):
                t = step / _length
                _pos = lerp(_old_position[0], self.center_x, t), lerp(_old_position[1], self._sprite.bottom, t)
                self._horizontal_sensor.position = _pos
                _collisions = self._horizontal_sensor.collides_with_list(self._chamber.sprite_lists['ground'])
                if len(_collisions):
                    self._on_ground = True
                    self._sprite.bottom = _collisions[0].top
                    self._velocity_y = 0.0
                    break

        if Input.get_button("ATTACK"):
            self._sprite.center_y += 3000

    def draw(self):
        self._sprite.draw(pixelated=True)

        # self._horizontal_sensor.center_x = self._sprite.center_x
        # self._horizontal_sensor.center_y = self._sprite.bottom
        # self._horizontal_sensor.draw(pixelated=True)
        # self._horizontal_sensor.center_y = self._sprite.top
        # self._horizontal_sensor.draw(pixelated=True)

        # self._vertical_sensor.center_y = self._sprite.center_y
        # self._vertical_sensor.center_x = self._sprite.left
        # self._vertical_sensor.draw(pixelated=True)
        # self._vertical_sensor.center_x = self._sprite.right
        # self._vertical_sensor.draw(pixelated=True)

    def horizontal_movement(self, _value: float):
        self._target_velocity_x = self._max_velocity * _value
        self._player_direction = self._player_direction if not _value else _value / abs(_value)

    def jump(self, button: Button):
        if self._on_ground:
            print(button)
            self._velocity_y = button.pressed * 512.0

    @property
    def center_x(self):
        return self._sprite.center_x

    @property
    def center_y(self):
        return self._sprite.center_y

    @property
    def position(self):
        return self._sprite.position
