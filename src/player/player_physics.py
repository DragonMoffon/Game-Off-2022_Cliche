from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from src.player.player import PlayerCharacter
    from src.player.player_states import PlayerStateSwitch

from arcade import SpriteList

from src.player.player_data import PlayerData
from src.player.player_hitbox import PlayerHitbox

from src.clock import Clock


class PlayerPhysics:

    def __init__(self, _source: "PlayerCharacter"):
        self._source: "PlayerCharacter" = _source
        self._state_switch: "PlayerStateSwitch" = _source.p_state_switch
        self._hitbox: PlayerHitbox = _source.p_hitbox
        self._data: PlayerData = _source.p_data

    def resolve_spike_collision(self, _collision_layer: SpriteList):
        return self._hitbox.hit_spike(_collision_layer)

    def resolve_collisions(self, _collision_layers: Tuple[SpriteList, SpriteList, SpriteList, SpriteList]):
        self._data.on_ground = self._data.on_ciel = self._data.on_left = self._data.on_right = False
        _ground_collision = _ciel_collision = _left_collision = _right_collision = None

        # Collides downward
        _hit = False
        if self._data.vel_y <= 0.0:
            _hit, _ground_collision = self._hitbox.hit_ground(_collision_layers[0])
            if _hit and self._data.old_bottom >= _ground_collision.top:
                self._state_switch.collision_bottom(_ground_collision)
                self._data.bottom = _ground_collision.top
                self._data.on_ground = True

                self._data.forgiven_edge_frames = Clock.frame
                self._data.forgiven_jump_frames = 0

        # Collides upward
        _hit = False
        if self._data.vel_y >= 0.0:
            _hit, _ciel_collision = self._hitbox.hit_ciel(_collision_layers[1])
            if _hit and self._data.old_top <= _ciel_collision.bottom:
                self._state_switch.collision_top(_ciel_collision)
                self._data.top = _ciel_collision.bottom
                self._data.on_ciel = True

        # Collides on the left
        _hit = False
        if self._data.vel_x <= 0.0:
            _hit, _left_collision = self._hitbox.hit_left(_collision_layers[2])
            if _hit and self._data.old_left >= _left_collision.right:
                self._state_switch.collision_left(_left_collision)
                self._data.left = _left_collision.right
                self._data.on_left = True

        # Collides on the right
        _hit = False
        if self._data.vel_x >= 0.0:
            _hit, _right_collision = self._hitbox.hit_right(_collision_layers[3])
            if _hit and self._data.old_right <= _right_collision.left:
                self._state_switch.collision_right(_right_collision)
                self._data.right = _right_collision.left
                self._data.on_right = True

    def move(self):
        self._data.old_pos = self._data.pos
        self._data.pos = (self._data.x + self._data.vel_x * Clock.delta_time,
                          self._data.y + self._data.vel_y * Clock.delta_time)
