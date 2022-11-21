from typing import List, Set, Dict, Type

from random import random

from arcade import Sprite, SpriteList, Texture, load_texture
from pytiled_parser import ObjectLayer

from src.util import TILE_SIZE, lerp_point, sqr_dist, sqr_length, normalise, normalise_to_length
from src.clock import Clock


class Enemy:
    c_boar_textures: Texture = None
    c_snake_texture: Texture = None
    c_hornet_texture: Texture = None
    c_hornet_nest_texture: Texture = None

    def __init__(self, _sprite: Sprite, _name: str, parent: "EnemyManager", _health: int):
        if Enemy.c_boar_textures is None:
            Enemy.c_boar_textures = load_texture(":assets:/textures/characters/placeholder_enemies1.png")
            Enemy.c_snake_texture = load_texture(":assets:/textures/characters/placeholder_enemies2.png")
            Enemy.c_hornet_texture = load_texture(":assets:/textures/characters/placeholder_enemies3.png")
            Enemy.c_hornet_nest_texture = load_texture(":assets:/textures/characters/placeholder_enemies4.png")

        # Enemy renderer (arcade.Sprite)
        self._sprite = _sprite
        self._parent = parent

        # Enemy data
        self._name = _name

        self._max_health: int = _health
        self._health: int = _health

        self.temp: bool = False

        self._spawn_position = _sprite.position

        self._death_listeners: Set[classmethod] = set()

    def hit(self):
        raise NotImplementedError()

    def process_logic(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def append_death_listener(self, listener):
        self._death_listeners.add(listener)

    def remove_death_listener(self, listener):
        self._death_listeners.discard(listener)

    def die(self):
        self._parent.enemy_killed(self)

        for listener in tuple(self._death_listeners):
            listener(self)

    @property
    def name(self):
        return self._name

    @property
    def sprite(self):
        return self._sprite


class BoarEnemy(Enemy):

    def __init__(self, _sprite: Sprite, _name: str, _parent: "EnemyManager", **data):
        super().__init__(_sprite, _name, _parent, data.get('health', 4))

        self._trot_target = self._sprite.center_x
        self._trot_min = data.get('trot_min', 0.0)
        self._trot_max = data.get('trot_max', 0.0)

    def hit(self):
        print(f"hit {self.name}")

    def process_logic(self):
        diff = self._sprite.center_x - self._trot_target
        if diff:
            pass
        else:
            pass
        pass

    def update(self):
        pass


class HornetEnemy(Enemy):
    c_max_acc: float = 14.0 * TILE_SIZE
    c_max_vel: float = 6.0 * TILE_SIZE
    c_max_jitter: float = 10.0 * TILE_SIZE
    c_max_jitter_len: float = 0.2

    def __init__(self, _sprite: Sprite, _name: str, _parent: "EnemyManager", **data):
        super().__init__(_sprite, _name, _parent, data.get('health', 1))

        self._circle_target = data.get('target', self._sprite.position)

        self._acc = (0.0, 0.0)
        self._vel = (0.0, 0.0)

        self._last_jitter = 0.0
        self._jitter_len = 0.0
        self._jitter_acc = 0.0, 0.0

    def hit(self):
        if self._max_health > 0:
            self._health -= 1
            if not self._health:
                self.die()

    def process_logic(self):
        _diff = self._circle_target[0] - self._sprite.center_x, self._circle_target[1] - self._sprite.center_y
        if sqr_length(_diff) == 0:
            self._acc = normalise_to_length((random(), random()), self.c_max_acc)
        else:
            if Clock.length(self._last_jitter) >= self._jitter_len:
                self._jitter_len = random() * self.c_max_jitter_len
                self._last_jitter = Clock.time

                self._jitter_acc = random() * self.c_max_jitter, random() * self.c_max_jitter

            _acc = normalise_to_length(_diff, self.c_max_acc)
            self._acc = _acc[0] + self._jitter_acc[0], _acc[1] + self._jitter_acc[1]

    def update(self):
        _vel = self._vel[0] + self._acc[0] * Clock.delta_time, self._vel[1] + self._acc[1] * Clock.delta_time
        if sqr_length(_vel) > self.c_max_vel**2:
            _vel = normalise_to_length(_vel, self.c_max_vel)
        self._vel = _vel

        _pos = self._sprite.position
        self._sprite.position = _pos[0] + self._vel[0] * Clock.delta_time, _pos[1] + self._vel[1] * Clock.delta_time


class HornetNestEnemy(Enemy):

    def __init__(self, _sprite: Sprite, _name: str, _parent: "EnemyManager", **data):
        super().__init__(_sprite, _name, _parent, data.get('health', 6))

        spawn_target = data['spawn_target'].split(" ")
        self._spawn_target = float(spawn_target[0]), float(spawn_target[1])
        self._spawn_max_dist = data['spawn_max_dist']

        self._spawn: Dict[str, HornetEnemy] = dict()

    def hit(self):
        print(f"hit {self.name}")

    def process_logic(self):
        if not len(self._spawn):
            self._spawn_hornet()

    def update(self):
        pass

    def _spawn_hornet(self):
        _sprite = Sprite(texture=self.c_hornet_texture)
        _sprite.position = self._sprite.position
        _data = {'target': self._spawn_target, 'max_dist': self._spawn_max_dist}
        _hornet_spawn = HornetEnemy(_sprite, f"hornet_spawn_{len(self._spawn) + 1}", self._parent, **_data)
        _hornet_spawn.temp = True

        _hornet_spawn.append_death_listener(self._hornet_die)

        self._spawn[_hornet_spawn.name] = _hornet_spawn

        self._parent.add_enemy(_hornet_spawn)

    def _hornet_die(self, _hornet: HornetEnemy):
        self._spawn.pop(_hornet.name)
        _hornet.remove_death_listener(self._hornet_die)


class SnakeEnemy(Enemy):

    def __init__(self, _sprite: Sprite, _name: str, _parent: "EnemyManager", **data):
        super().__init__(_sprite, _name, _parent, data.get('health', -1))

    def hit(self):
        print(f"hit {self.name}")

    def process_logic(self):
        pass

    def update(self):
        pass


class EnemyManager:
    c_enemy_type_classes: Dict[str, Type[Enemy]] = {'boar': BoarEnemy, 'snake': SnakeEnemy,
                                                    'hornet': HornetEnemy, 'nest': HornetNestEnemy}

    def __init__(self, _layer_data: ObjectLayer, _sprites: SpriteList):
        self._sprites = _sprites
        self._enemies: Dict[str, Enemy] = dict()
        self._enemy_sprite_map: Dict[Sprite, Enemy] = dict()

        self._killed_enemies: Dict[str, Enemy] = dict()

        for _index, _object in enumerate(_layer_data.tiled_objects):
            _new_enemy = self.c_enemy_type_classes[_object.properties['type']](_sprites[_index], _object.name,
                                                                               self, **_object.properties)
            self._enemies[_object.name] = _new_enemy
            self._enemy_sprite_map[_sprites[_index]] = _new_enemy

    def process_enemy_logic(self):
        for _enemy in tuple(self._enemies.values()):
            _enemy.process_logic()

    def update_enemies(self):
        for _enemy in tuple(self._enemies.values()):
            _enemy.update()

    def enemy_killed(self, _enemy: Enemy):
        print(_enemy)
        self._enemies.pop(_enemy.name)
        self._enemy_sprite_map.pop(_enemy.sprite)
        self._sprites.remove(_enemy.sprite)

        if not _enemy.temp:
            self._killed_enemies[_enemy.name] = _enemy

    def add_enemy(self, _enemy: Enemy):
        if not _enemy.temp:
            self._killed_enemies.pop(_enemy.name)
        self._sprites.append(_enemy.sprite)
        self._enemies[_enemy.name] = _enemy
        self._enemy_sprite_map[_enemy.sprite] = _enemy

    def enemy_hit(self, _enemy_sprite: Sprite):
        self._enemy_sprite_map[_enemy_sprite].hit()

    @property
    def sprites(self):
        return self._sprites

    @property
    def enemies(self):
        return self._enemies

