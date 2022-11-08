from arcade import Sprite, SpriteSolidColor, SpriteList, load_texture

from src.map.chamber import Chamber

from src.player.player_data import PlayerData
from src.player.player_hitbox import PlayerHitbox

from src.input import Input, Button
from src.clock import Clock

# TODO: Complete Input Code and Physics integration


class PlayerCharacter:
    """
    PlayerCharacter holds every part of the player in the game world, and only handles input. The movement is done
    in the physics engine, and the sprite at the core draws everything.
    """

    def __init__(self, _chamber: Chamber):
        # TODO: make actual sprite and setup animations

        self._sprite = Sprite(texture=load_texture(":assets:/textures/characters/placeholder_player.png"))
        self._data = PlayerData(self._sprite)
        self._data.bottom = 192.0
        self._data.left = 128.0

        self._hitbox = PlayerHitbox(self._sprite, self._data)

        # TODO: remove placeholder variables
        self._horizontal_sensor = SpriteSolidColor(int(abs(self._sprite.right - self._sprite.left)-4), 1, (255, 0, 0))
        self._vertical_sensor = SpriteSolidColor(1, int(abs(self._sprite.top - self._sprite.bottom)-4), (0, 255, 0))

        self._chamber: Chamber = _chamber

        Input.get_axis("HORIZONTAL").register_observer(self.horizontal_movement)
        Input.get_button("JUMP").register_press_observer(self.jump)
        Input.get_button("CROUCH").register_press_observer(self.crouch)

    def update(self):
        # Calculate Acceleration
        if Input.get_button("SPRINT"):
            _target_velocity_x = (max(abs(self._data.vel_x), self._data.c_max_vel_sprint)
                                  * self._data.direction * bool(Input.get_axis("HORIZONTAL")))
        else:
            _target_velocity_x = self._data.c_max_vel * Input.get_axis("HORIZONTAL")

        _diff = _target_velocity_x - self._data.vel_x
        _acceleration = self._data.c_max_dec
        if _target_velocity_x:
            if self._data.vel_x / _target_velocity_x < 0:
                _acceleration = self._data.c_max_turn
            else:
                _acceleration = self._data.c_max_acc

        _acceleration = min(abs(_diff), _acceleration * Clock.delta_time) * (_diff / abs(_diff)) if _diff else 0

        self._data.vel_x += _acceleration

        if not self._data.on_ground:
            self._data.vel_y -= 1024.0 * Clock.delta_time

        # move player
        self._data.old_pos = self._sprite.position
        self._data.x += self._data.vel_x * Clock.delta_time
        self._data.y += self._data.vel_y * Clock.delta_time

        # Collisions
        self._data.on_ground = self._data.on_ciel = self._data.on_left = self._data.on_right = False
        _chamber_ground = self._chamber.sprite_lists['ground']
        _chamber_one_way = self._chamber.sprite_lists['one_way']
        _ground_collision = _ciel_collision = _left_collision = _right_collision = None

        _all_tiles = SpriteList(lazy=True, use_spatial_hash=True)
        _all_tiles.extend(_chamber_ground)
        if not Input.get_button("CROUCH"):
            _all_tiles.extend(_chamber_one_way)

        # Collides downward
        _hit = False
        if self._data.vel_y <= 0.0:
            _hit, _ground_collision = self._hitbox.hit_ground(_all_tiles)
            if _hit and self._data.old_bottom >= _ground_collision.top:
                self._data.vel_y = max(self._data.vel_y, 0.0)
                self._data.bottom = _ground_collision.top
                self._data.on_ground = True

                self._data.forgiven_edge_frames = 15

        # Collides upward
        _hit = False
        if self._data.vel_y >= 0.0:
            _hit, _ciel_collision = self._hitbox.hit_ciel(_chamber_ground)
            if _hit and self._data.old_top <= _ciel_collision.bottom:
                self._data.vel_y = min(self._data.vel_y, 0.0)
                self._data.top = _ciel_collision.bottom
                self._data.on_ciel = True

        # Collides on the left
        _hit = False
        if self._data.vel_x <= 0.0:
            _hit, _left_collision = self._hitbox.hit_left(_chamber_ground)
            if _hit and self._data.old_left >= _left_collision.right:
                self._data.vel_x = max(self._data.vel_x, 0.0)
                self._data.left = _left_collision.right
                self._data.on_left = True

        # Collides on the right
        _hit = False
        if self._data.vel_x >= 0.0:
            _hit, _right_collision = self._hitbox.hit_right(_chamber_ground)
            if _hit and self._data.old_right <= _right_collision.left:
                self._data.vel_x = min(self._data.vel_x, 0.0)
                self._data.right = _right_collision.left
                self._data.on_right = True

        if not self._data.on_ground and self._data.forgiven_edge_frames:
            self._data.forgiven_edge_frames -= 1
        elif self._data.on_ground and Clock.frame_length(Input.get_button("JUMP").release_frame) <= 12:
            self._data.vel_y = 512.0
            self._data.forgiven_edge_frames = 0

        self._data.on_ledge = False
        if not self._data.on_ground and self._data.vel_y <= 0.0 and not self._data.blocked_ledge_frames:
            self._data.blocked_ledge_frames = 0
            if (self._data.on_left and self._data.direction == -1 and
                    self._hitbox.check_ledge_vertical_left(_chamber_ground)):
                self._data.vel_y = 0.0
                self._data.on_ledge = True
                self._data.top = _left_collision.top
            elif (self._data.on_right and self._data.direction == 1 and
                  self._hitbox.check_ledge_vertical_right(_chamber_ground)):
                self._data.vel_y = 0.0
                self._data.on_ledge = True
                self._data.top = _right_collision.top
        elif self._data.blocked_ledge_frames:
            self._data.blocked_ledge_frames -= 1

    def draw(self):
        self._sprite.draw(pixelated=True)

        self._hitbox.debug_draw()

    def horizontal_movement(self, _value: float):
        self._data.direction = self._data.direction if not _value else _value / abs(_value)

    def jump(self, button: Button):
        if self._data.on_ground or self._data.forgiven_edge_frames or self._data.on_ledge:
            self._data.vel_y = button.pressed * (512.0 + 512.0 * self._data.on_ledge)
            self._data.forgiven_edge_frames = 0.0
            self._data.blocked_ledge_frames = self._data.c_ledge_buffer_frames
        elif self._data.on_right and not self._data.on_left:
            self._data.vel_y = button.pressed * 512.0 * 1.5
            self._data.vel_x = button.pressed * (-256.0 - 768.0 * Input.get_button("SPRINT"))
        elif self._data.on_left and not self._data.on_right:
            self._data.vel_y = button.pressed * 512.0 * 1.5
            self._data.vel_x = button.pressed * (256.0 + 768.0 * Input.get_button("SPRINT"))

    def crouch(self, button: Button):
        if button and self._data.on_ledge:
            self._data.blocked_ledge_frames = self._data.c_ledge_buffer_frames
            self._data.vel_y = -512.0


    @property
    def center_x(self):
        return self._sprite.center_x

    @property
    def center_y(self):
        return self._sprite.center_y

    @property
    def position(self):
        return self._sprite.position
