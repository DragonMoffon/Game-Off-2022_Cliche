from arcade import Sprite, SpriteSolidColor, SpriteList, load_texture

from src.map.chamber import Chamber

from src.player.player_data import PlayerData
from src.player.player_hitbox import PlayerHitbox
from src.player.player_states import PlayerStateSwitch
from src.player.player_physics import PlayerPhysics

from src.input import Input, Button
from src.clock import Clock

from time import time

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
        self._physics = PlayerPhysics(self)
        self._states = PlayerStateSwitch(self)

        # TODO: remove placeholder variables

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
            self._data.vel_y -= (1024.0 - (256.0 * (Input.get_button("JUMP") and self._data.vel_y >= 0.0))) * Clock.delta_time

        # move player
        self._physics.move()

        # Collisions
        _ground = self._chamber.sprite_lists['ground']
        _all_tiles = self._chamber.sprite_lists['all_ground'] if not Input.get_button("CROUCH") else _ground
        self._physics.resolve_collisions((_all_tiles, _ground, _ground, _ground))

        if not self._data.on_ground and self._data.forgiven_edge_frames:
            self._data.forgiven_edge_frames -= 1
        elif self._data.on_ground and Clock.frame_length(Input.get_button("JUMP").release_frame) <= 12:
            self._data.vel_y = 512.0
            self._data.forgiven_edge_frames = 0

        # self._data.at_ledge = False
        # if not self._data.on_ground and self._data.vel_y <= 0.0 and not self._data.blocked_ledge_frames:
        #     self._data.blocked_ledge_frames = 0
        #     if (self._data.on_left and self._data.direction == -1 and
        #             self._hitbox.check_ledge_vertical_left(_chamber_ground)):
        #         self._data.vel_y = 0.0
        #         self._data.at_ledge = True
        #         self._data.top = _left_collision.top
        #     elif (self._data.on_right and self._data.direction == 1 and
        #           self._hitbox.check_ledge_vertical_right(_chamber_ground)):
        #         self._data.vel_y = 0.0
        #         self._data.at_ledge = True
        #         self._data.top = _right_collision.top
        # elif self._data.blocked_ledge_frames:
        #     self._data.blocked_ledge_frames -= 1

        self._states.find_state()

    def draw(self):
        self._sprite.draw(pixelated=True)

        self._hitbox.debug_draw()

    def horizontal_movement(self, _value: float):
        self._data.direction = self._data.direction if not _value else _value / abs(_value)

    def jump(self, button: Button):
        if self._data.on_ground or self._data.forgiven_edge_frames or self._data.at_ledge:
            self._data.vel_y = button.pressed * (512.0 + 512.0 * self._data.at_ledge * Input.get_button("SPRINT"))
            self._data.forgiven_edge_frames = 0.0
            self._data.blocked_ledge_frames = self._data.c_ledge_buffer_frames
        elif self._data.on_right and not self._data.on_left:
            self._data.vel_y = button.pressed * 512.0 * 1.5
            self._data.vel_x = button.pressed * (-512.0 - 512.0 * Input.get_button("SPRINT"))
        elif self._data.on_left and not self._data.on_right:
            self._data.vel_y = button.pressed * 512.0 * 1.5
            self._data.vel_x = button.pressed * (512.0 + 512.0 * Input.get_button("SPRINT"))

    def crouch(self, button: Button):
        if button and self._data.at_ledge:
            self._data.blocked_ledge_frames = self._data.c_ledge_buffer_frames
            self._data.vel_y = -128.0


    @property
    def center_x(self):
        return self._sprite.center_x

    @property
    def center_y(self):
        return self._sprite.center_y

    @property
    def position(self):
        return self._sprite.position
