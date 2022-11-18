from typing import Tuple

from arcade import Sprite, SpriteSolidColor, load_texture, Texture

from src.player.player_data import PlayerData

from src.clock import Clock
from src.input import Input
from src.worldmap import Map

from src.util import TILE_SIZE


class PlayerHit(Sprite):
    c_hit_texture: Texture = None

    c_hit_max_age: int = 4

    def __init__(self):
        if not self.c_hit_texture:
            self.c_hit_texture = load_texture(":assets:/textures/characters/placeholder_hit.png")
        super().__init__()
        self.texture = self.c_hit_texture


class PlayerAttack:
    c_attack_max_age: int = 8
    c_knockback = 8.0 * TILE_SIZE

    def __init__(self, _data: PlayerData, _sprite: Sprite, _hitbox: SpriteSolidColor,
                 rel_pos: Tuple[float, float], hitbox_pos: Tuple[float, float]):
        self._data: PlayerData = _data

        self._sprite = _sprite
        self._hitbox = _hitbox

        self._rel_pos = rel_pos
        self._hitbox_pos = hitbox_pos

        self._hit: Sprite = None

        # TODO: Add animation system
        self._animator = None

        self._spawn_frame = Clock.frame

        self._struck = False

    def update_position(self):
        self._hitbox.position = self._data.x + self._hitbox_pos[0], self._data.y + self._hitbox_pos[1]
        self._sprite.position = self._data.x + self._rel_pos[0], self._data.y + self._rel_pos[1]

    def check_collision_environment(self):
        return self._hitbox.collides_with_list(Map.current.dangers['spikes'])

    def check_collision_enemies(self):
        return self._hitbox.collides_with_list(Map.current.enemies.sprites)

    def check_attack(self):
        raise NotImplementedError()

    def check_should_live(self):
        return Clock.frame_length(self._spawn_frame) <= self.c_attack_max_age

    def animate(self):
        raise NotImplementedError()

    def draw(self):
        # self._hitbox.draw(pixelated=True)
        self._sprite.draw(pixelated=True)
        if self._hit:
            self._hit.draw(pixelated=True)


class DownAttack(PlayerAttack):

    def __init__(self, _data: PlayerData, _sprite: Sprite, _hitbox: SpriteSolidColor):
        super().__init__(_data, _sprite, _hitbox, (0.0, -22.0), (0.0, -34.0))

    def animate(self):
        raise NotImplementedError()

    def check_attack(self):
        if not self._struck:
            self.update_position()

            enemy_collisions = self.check_collision_enemies()

            terrain_collisions = self.check_collision_environment()

            if enemy_collisions:
                self._struck = True
                self._hit = PlayerHit()
                self._hit.bottom = enemy_collisions[0].top
                self._hit.center_x = self._data.x
                if Input.get_button("DASH"):
                    print("dash slash")
                    return [self._data.vel_x // 1.5, abs(self._data.vel_x) * 1.5 + self.c_knockback]
                else:
                    return [self._data.vel_x, self.c_knockback]
            elif terrain_collisions:
                self._struck = True
                self._hit = PlayerHit()
                self._hit.bottom = terrain_collisions[0].top
                self._hit.center_x = self._data.x
                return [self._data.vel_x, self.c_knockback]
        return self._data.vel


class RightAttack(PlayerAttack):

    def __init__(self, _data: PlayerData, _sprite: Sprite, _hitbox: SpriteSolidColor):
        super().__init__(_data, _sprite, _hitbox, (52.0, 0.0), (70.0, 0.0))

    def animate(self):
        raise NotImplementedError()

    def check_attack(self):
        if not self._struck:
            self.update_position()

            enemy_collisions = self.check_collision_enemies()

            terrain_collisions = self.check_collision_environment()

            if enemy_collisions:
                self._struck = True
                self._hit = PlayerHit()
                self._hit.angle = 90.0
                self._hit.right = enemy_collisions[0].left
                self._hit.center_y = self._data.y

                if Input.get_button("DASH"):
                    print("dash slash")
                    return [-abs(self._data.vel_y) * 1.5 - self.c_knockback, abs(self._data.vel_y) // 1.5]
                else:
                    return [-self.c_knockback, self._data.vel_y]
            elif terrain_collisions:
                self._struck = True
                self._hit = PlayerHit()
                self._hit.angle = 90.0
                self._hit.right = terrain_collisions[0].left
                self._hit.center_y = self._data.y

                return [-self.c_knockback, self._data.vel_y]
        return self._data.vel


class LeftAttacK(PlayerAttack):

    def __init__(self, _data: PlayerData, _sprite: Sprite, _hitbox: SpriteSolidColor):
        super().__init__(_data, _sprite, _hitbox, (-52.0, 0.0), (-70.0, 0.0))

    def animate(self):
        raise NotImplementedError()

    def check_attack(self):
        if not self._struck:
            self.update_position()

            enemy_collisions = self.check_collision_enemies()

            terrain_collisions = self.check_collision_environment()

            if enemy_collisions:
                self._struck = True
                self._hit = PlayerHit()
                self._hit.angle = -90.0
                self._hit.left = enemy_collisions[0].right
                self._hit.center_y = self._data.y

                if Input.get_button("DASH"):
                    print("dash slash")
                    return [abs(self._data.vel_y) * 1.5 + self.c_knockback, abs(self._data.vel_y) // 1.5]
                else:
                    return [self.c_knockback, self._data.vel_y]
            elif terrain_collisions:
                self._struck = True
                self._hit = PlayerHit()
                self._hit.angle = -90.0
                self._hit.left = terrain_collisions[0].right
                self._hit.center_y = self._data.y

                return [self.c_knockback, self._data.vel_y]
        return self._data.vel


class PlayerWeapon:
    c_attack_delay: int = 16

    def __init__(self, _data: PlayerData):
        self._data: PlayerData = _data

        self._side_swipe = load_texture(":assets:/textures/characters/placeholder_player_attack.png",
                                        width=128, height=128)
        self._down_swipe = load_texture(":assets:/textures/characters/placeholder_player_attack.png",
                                        width=128, height=128, x=128)

        self._side_hitbox: SpriteSolidColor = SpriteSolidColor(128, 96, (255, 255, 255))
        self._down_hitbox: SpriteSolidColor = SpriteSolidColor(96, 128, (255, 255, 255))

        self._current_attack: PlayerAttack = None

        self._last_attack: int = 0
        self._sprite: Sprite = Sprite(texture=self._down_swipe)

    def draw(self):
        if self._current_attack:
            self._current_attack.draw()

    def update(self):
        if self._current_attack and self._current_attack.check_should_live():
            self._data.vel = self._current_attack.check_attack()

            self._last_attack = Clock.frame
        else:
            self._current_attack = None

    def attack_downward(self):
        if not self._current_attack and Clock.frame_length(self._last_attack) > self.c_attack_delay:
            self._last_attack = 0
            self._sprite.scale_xy = (1.0, 1.0)
            self._sprite.texture = self._down_swipe
            self._current_attack = DownAttack(self._data, self._sprite, self._down_hitbox)
            self._current_attack.update_position()

    def attack_left(self):
        if not self._current_attack and Clock.frame_length(self._last_attack) > self.c_attack_delay:
            self._last_attack = 0
            self._sprite.scale_xy = (-1.0, 1.0)
            self._sprite.texture = self._side_swipe
            self._current_attack = LeftAttacK(self._data, self._sprite, self._side_hitbox)
            self._current_attack.update_position()

    def attack_right(self):
        if not self._current_attack and Clock.frame_length(self._last_attack) > self.c_attack_delay:
            self._last_attack = 0
            self._sprite.scale_xy = (1.0, 1.0)
            self._sprite.texture = self._side_swipe
            self._current_attack = RightAttack(self._data, self._sprite, self._side_hitbox)
            self._current_attack.update_position()

