from arcade import Sprite, SpriteSolidColor, tilemap, SpriteList

from src.player.player_data import PlayerData
from src.player.player_hitbox import PlayerHitbox

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
        self._data = PlayerData(self._sprite)
        self._data.bottom = 192.0
        self._data.left = 128.0

        self._hitbox = PlayerHitbox(self._sprite, self._data)

        # TODO: remove placeholder variables
        self._horizontal_sensor = SpriteSolidColor(int(abs(self._sprite.right - self._sprite.left)-4), 1, (255, 0, 0))
        self._vertical_sensor = SpriteSolidColor(1, int(abs(self._sprite.top - self._sprite.bottom)-4), (0, 255, 0))

        self._chamber: tilemap.TileMap = _chamber

        self._player_acceleration = 15.0 * 32.0
        self._player_deceleration = 30.0 * 32.0
        self._player_turn = 60.0 * 32.0

        self._player_direction = 0.0
        self._max_velocity = 10.0 * 32.0
        self._target_velocity_x = 0.0

        self._on_ground = self._on_ciel = self._on_left = self._on_right = True

        Input.get_axis("HORIZONTAL").register_observer(self.horizontal_movement)
        Input.get_button("JUMP").register_press_observer(self.jump)

    def update(self):

        # Calculate Acceleration
        _diff = self._target_velocity_x - self._data.vel_x
        _acceleration = self._player_deceleration
        if self._target_velocity_x:
            if self._data.vel_x / self._target_velocity_x < 0:
                _acceleration = self._player_turn
            else:
                _acceleration = self._player_acceleration

        _acceleration = min(abs(_diff), _acceleration * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        self._data.vel_x += _acceleration

        if not self._on_ground:
            self._data.vel_y -= 1024.0 * Clock.delta_time

        # move player
        self._data.old_pos = self._sprite.position
        self._data.x += self._data.vel_x * Clock.delta_time
        self._data.y += self._data.vel_y * Clock.delta_time

        # Collisions
        self._on_ground = self._on_ciel = self._on_left = self._on_right = False
        _chamber_ground = self._chamber.sprite_lists['ground']
        _chamber_one_way = self._chamber.sprite_lists['one_way']
        _ground_collision = _ciel_collision = _left_collision = _right_collision = None

        # Collides downward
        _hit = False
        if self._data.vel_y <= 0.0:
            _all_tiles = SpriteList(lazy=True, use_spatial_hash=True)
            _all_tiles.extend(_chamber_ground)
            _all_tiles.extend(_chamber_one_way)
            _hit, _ground_collision = self._hitbox.hit_ground(_all_tiles)
            if _hit:
                self._data.vel_y = max(self._data.vel_y, 0.0)
                if self._data.old_bottom >= _ground_collision.top:
                    self._data.bottom = _ground_collision.top
                    self._on_ground = True

        # Collides upward
        _hit = False
        if self._data.vel_y >= 0.0:
            _hit, _ciel_collision = self._hitbox.hit_ciel(_chamber_ground)
            if _hit:
                self._data.vel_y = min(self._data.vel_y, 0.0)
                if self._data.old_top <= _ciel_collision.bottom:
                    self._data.top = _ciel_collision.bottom
                    self._on_ciel = True

        # Collides on the left
        _hit = False
        if self._data.vel_x <= 0.0:
            _hit, _left_collision = self._hitbox.hit_left(_chamber_ground)
            if _hit:
                self._data.vel_x = max(self._data.vel_x, 0.0)
                print(self._data.old_left, _left_collision.right)
                if self._data.old_left >= _left_collision.right:
                    self._data.left = _left_collision.right
                    self._on_left = True

        # Collides on the right
        _hit = False
        if self._data.vel_x >= 0.0:
            _hit, _right_collision = self._hitbox.hit_right(_chamber_ground)
            if _hit:
                self._data.vel_x = min(self._data.vel_x, 0.0)
                if self._data.old_right <= _right_collision.left:
                    self._data.right = _right_collision.left
                    self._on_right = True

        if Input.get_button("ATTACK"):
            self._sprite.center_y += 3000

    def draw(self):
        self._sprite.draw(pixelated=True)

        self._hitbox.debug_draw()

    def horizontal_movement(self, _value: float):
        self._target_velocity_x = self._max_velocity * _value
        self._player_direction = self._player_direction if not _value else _value / abs(_value)

    def jump(self, button: Button):
        if self._on_ground:
            self._data.vel_y = button.pressed * 512.0
        elif self._on_right and not self._on_left:
            self._data.vel_y = button.pressed * 512.0
            self._data.vel_x = button.pressed * -1024.0
        elif self._on_left and not self._on_right:
            self._data.vel_y = button.pressed * 512.0
            self._data.vel_x = button.pressed * 1024.0

    @property
    def center_x(self):
        return self._sprite.center_x

    @property
    def center_y(self):
        return self._sprite.center_y

    @property
    def position(self):
        return self._sprite.position
