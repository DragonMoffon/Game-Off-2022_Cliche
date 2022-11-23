from arcade import Sprite, load_texture

from src.player.player_data import PlayerData, PlayerAnimator, Player16pxParticleAnimator
from src.player.player_hitbox import PlayerHitbox
from src.player.player_states import PlayerStateSwitch
from src.player.player_physics import PlayerPhysics
from src.player.player_weapon import PlayerWeapon

from src.worldmap import Map

from src.input import Input, Button

# TODO: Complete Input Code and Physics integration


class PlayerCharacter:
    """
    PlayerCharacter holds every part of the player in the game world, and only handles input. The movement is done
    in the physics engine, and the sprite at the core draws everything.
    """

    def __init__(self):
        # TODO: make actual sprite and setup animations

        self._sprite = Sprite(texture=load_texture(":assets:/textures/characters/player/player.png"))
        self._sprite.set_hit_box(((-16, -32), (-16, 32), (16, 32), (16, -32)))
        self._data = PlayerData(self._sprite)
        self._data.bottom = 192.0
        self._data.left = 128.0

        Player16pxParticleAnimator.load(":assets:/textures/particles", "placeholder_particle_16px")

        # PlayerAnimator.load(":assets:/textures/characters/enemies/animations/", "boar_animation", self._sprite)

        # PlayerAnimator.set_state('walk')

        self._weapon = PlayerWeapon(self._data)

        self._states = PlayerStateSwitch(self)

        self._hitbox = PlayerHitbox(self._sprite, self._data)
        self._physics = PlayerPhysics(self)

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
        _ground = Map.current.ground['ground']
        _all_tiles = Map.current.ground['all_ground'] if not Input.get_button("CROUCH") else _ground
        self._physics.resolve_collisions((_all_tiles, _ground, _ground, _ground))

        _spikes = Map.current.dangers['spikes']
        _hit_spikes = self._hitbox.hit_spike(_spikes)
        if len(_hit_spikes):
            self._data.reset_to_ground()

        _spawn_zone = Map.current.spawn_zones
        _hit_zones = self._hitbox.hit_spawn_zone(_spawn_zone)
        self._data.in_spawn_zone = False
        if len(_hit_zones):
            self._data.in_spawn_zone = True

        # Find the next state
        self._states.find_state()

        # Manage weapon
        self._weapon.update()

        # Animate
        self._sprite.scale_xy = [self._data.direction, 1.0]

        self._states.debug_update_pos()

        if self._data.on_ground and self._data.in_spawn_zone:
            self._data.set_last_ground()

        self._check_map_transition()

        Player16pxParticleAnimator.update()
        Player16pxParticleAnimator.animate()
        # PlayerAnimator.animate()

    def draw(self):
        self._sprite.draw(pixelated=True)

        self._hitbox.debug_draw()
        # self._sprite.draw_hit_box((255, 255, 255), 2)
        self._states.debug_draw()
        self._weapon.draw()
        Player16pxParticleAnimator.draw()

    def _check_map_transition(self):
        _gate_collision = Map.current.should_transition(self._sprite)
        if _gate_collision:
            if self._data.can_transition:
                self._data.can_transition = False
                _next_room, self._data.pos = _gate_collision.transition(self._data)
                self._data.set_last_ground_instant()

                Map.set_room(_next_room)
        else:
            self._data.can_transition = True

    @property
    def position(self):
        return self._sprite.position

    @property
    def p_sprite(self):
        return self._sprite

    @property
    def p_data(self):
        return self._data

    @property
    def p_hitbox(self):
        return self._hitbox

    @property
    def p_weapon(self):
        return self._weapon

    @property
    def p_state_switch(self):
        return self._states

    @property
    def p_physics(self):
        return self._physics
