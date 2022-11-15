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
        self._sprite.set_hit_box(((-16, -32), (-16, 32), (16, 32), (16, -32)))
        self._data = PlayerData(self._sprite)
        self._data.bottom = 192.0
        self._data.left = 128.0

        self._states = PlayerStateSwitch(self)

        self._hitbox = PlayerHitbox(self._sprite, self._data)
        self._physics = PlayerPhysics(self)

        # TODO: remove placeholder variables

        self._chamber: Chamber = _chamber

        Input.get_axis("HORIZONTAL").register_observer(self.horizontal_movement)
        Input.get_button("JUMP").register_press_observer(self.jump)
        Input.get_button("CROUCH").register_press_observer(self.crouch)
        Input.get_button("RESET").register_press_observer(self.reset)

    def reset(self, _button: Button):
        if _button:
            self._data.reset_to_ground()

    def update(self):
        # Update based on the state
        self._states.state_update()

        # Move player
        self._physics.move()

        # Collisions
        _ground = self._chamber.sprite_lists['ground']
        _all_tiles = self._chamber.sprite_lists['all_ground'] if not Input.get_button("CROUCH") else _ground
        self._physics.resolve_collisions((_all_tiles, _ground, _ground, _ground))

        _spikes = self._chamber.sprite_lists['spikes']
        _hit_spikes = self._hitbox.hit_spike(_spikes)
        if len(_hit_spikes):
            self._data.reset_to_ground()

        _spawn_zone = self._chamber.sprite_lists['spawn_zones']
        _hit_zones = self._hitbox.hit_spawn_zone(_spawn_zone)
        self._data.in_spawn_zone = False
        if len(_hit_zones):
            self._data.in_spawn_zone = True

        # Find the next state
        self._states.find_state()

        # Animate
        self._sprite.scale_xy = [self._data.direction, 1.0]

        self._states.debug_update_pos()

        if self._data.on_ground and self._data.in_spawn_zone:
            self._data.set_last_ground()

    def draw(self):
        self._sprite.draw(pixelated=True)

        self._hitbox.debug_draw()
        # self._sprite.draw_hit_box((255, 255, 255), 2)
        self._states.debug_draw()

    def horizontal_movement(self, _value: float):
        self._states.p_horizontal(_value)

    def jump(self, _button: Button):
        self._states.p_jump(_button)

    def crouch(self, _button: Button):
        self._states.p_crouch(_button)

    @property
    def center_x(self):
        return self._sprite.center_x

    @property
    def center_y(self):
        return self._sprite.center_y

    @property
    def position(self):
        return self._sprite.position

    @property
    def p_chamber(self):
        return self._chamber

    @property
    def p_data(self):
        return self._data

    @property
    def p_hitbox(self):
        return self._hitbox

    @property
    def p_state_switch(self):
        return self._states

    @property
    def p_physics(self):
        return self._physics
