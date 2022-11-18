from typing import Dict, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from src.player.player_data import PlayerData
from os import listdir

from arcade import tilemap, Sprite, SpriteList
from arcade.resources import resolve_resource_path

from src.enemies import EnemyManager

from src.util import TILE_SIZE, DEBUG

from threading import Thread


class Transition:

    def __init__(self, _tile: Dict, _sprite: Sprite):
        self._sprite = _sprite

        _region, _room = _tile['target room'].split(" ")
        self._target_region = _region
        self._target_room = _room
        self._target_gate = _tile['target entrance']

        self._direction = _tile['direction']
        self._id = _tile['entrance id']

    def __repr__(self):
        return f"{self._id} : {self._direction}"

    def check(self, sprite: Sprite):
        return sprite.collides_with_sprite(self._sprite)

    def transition(self, _player_data: "PlayerData"):
        _next_room = Map[self._target_region, self._target_room]
        _next_entrance = _next_room.gates[self._target_gate]

        _next_pos = (0, 0)

        if self._direction == 0:
            # Transition at top of screen
            rel_x = (_player_data.x - self.x) / self.width * _next_entrance.width
            return _next_room, (_next_entrance.x + rel_x, _next_entrance.top + _player_data.height)
        elif self._direction == 1:
            # Transition at right of screen
            rel_y = (_player_data.y - self.y) / self.height * _next_entrance.height
            return _next_room, (_next_entrance.right, _next_entrance.y + rel_y)
        elif self._direction == 2:
            # Transition at bottom of screen
            rel_x = (_player_data.x - self.x) / self.width * _next_entrance.width
            return _next_room, (_next_entrance.x + rel_x, _next_entrance.bottom - _player_data.height)
        elif self._direction == 3:
            # transition at left of screen
            rel_y = (_player_data.y - self.y) / self.height * _next_entrance.height
            return _next_room, (_next_entrance.left, _next_entrance.y + rel_y)

        raise ValueError(f"direction {self._direction} is not a valid direction")

    @property
    def x(self):
        return self._sprite.center_x

    @property
    def y(self):
        return self._sprite.center_y

    @property
    def top(self):
        return self._sprite.top

    @property
    def bottom(self):
        return self._sprite.bottom

    @property
    def left(self):
        return self._sprite.left

    @property
    def right(self):
        return self._sprite.right

    @property
    def width(self):
        return self._sprite.width

    @property
    def height(self):
        return self._sprite.height


class Room:

    def __init__(self, _name: str, _region: str, _map: tilemap.TileMap):
        self._name = _name
        self._region = _region

        # TODO: REMOVE MAP and ONLY STORE NECESSARY DATA
        self._map = _map

        self._tile_width = _map.width
        self._tile_height = _map.height

        self._transitions: Dict[int, Transition] = dict()
        _transition_list = _map.sprite_lists.pop('transitions')
        for _index, _object in enumerate(_map.tiled_map.layers[1].tiled_objects):
            _properties = _object.properties
            self._transitions[_properties['entrance id']] = Transition(_properties, _transition_list[_index])

        self._dangers: Dict[str, SpriteList] = {"spikes": _map.sprite_lists.pop('spikes')}
        self._enemies: EnemyManager = EnemyManager(_map.sprite_lists.get('enemies', SpriteList()))

        self._ground: Dict[str, SpriteList] = {"ground": _map.sprite_lists.pop('ground'),
                                               "one_way": _map.sprite_lists.pop('one_way')}
        _all_ground = SpriteList(use_spatial_hash=True)
        _all_ground.extend(self._ground['ground'])
        _all_ground.extend(self._ground['one_way'])
        self._ground['all_ground'] = _all_ground

        self._decorations: Dict[str, SpriteList] = {"background": _map.sprite_lists.pop('background'),
                                                    "decorations": _map.sprite_lists.pop('decorations')}

        self._spawn_zones: SpriteList = _map.sprite_lists.pop('spawn_zones')

    def __repr__(self):
        return f"{self._region}: {self._name}"

    def initialise(self):
        for _list in self._dangers.values():
            _list.initialize()

        self._enemies.sprites.initialize()

        for _list in self._ground.values():
            _list.initialize()

        self._spawn_zones.initialize()

    def draw(self):
        self._decorations['background'].draw(pixelated=True)
        self._ground["all_ground"].draw(pixelated=True)
        for danger in self._dangers.values():
            danger.draw(pixelated=True)
        self._enemies.sprites.draw(pixelated=True)
        self._decorations['decorations'].draw(pixelated=True)

    def should_transition(self, _other: Sprite):
        for transition in self._transitions.values():
            if transition.check(_other):
                return transition

    # Sprite lists and Dicts
    @property
    def gates(self):
        return self._transitions

    @property
    def ground(self):
        return self._ground

    @property
    def dangers(self):
        return self._dangers

    @property
    def enemies(self):
        return self._enemies

    @property
    def decorations(self):
        return self._decorations

    @property
    def spawn_zones(self):
        return self._spawn_zones

    # map data

    @property
    def tile_width(self):
        return self._tile_width

    @property
    def tile_height(self):
        return self._tile_height

    @property
    def px_width(self):
        return self._tile_width * TILE_SIZE

    @property
    def px_height(self):
        return self._tile_height * TILE_SIZE


class GameMap:
    c_src_base: str = ":assets:/tiled_maps"
    c_regions: Tuple[str, ...] = ("Test", "JungleEdge") # ("JungleEdge", "JungleBranches", "TempleHeart", "TempleDepths", "JungleFloor", "Test")

    def __init__(self):
        self._regions: Dict[str, Dict[str, Room]] = {_region: dict() for _region in self.c_regions}
        self._current_room: Room = None

    def initialise(self):
        def load_rooms(region: str):
            print("started:", region)
            _src = resolve_resource_path(self.c_src_base + f"/{region}")
            _rooms = listdir(_src)
            for _room in _rooms:
                if _room.endswith('.tmj'):
                    _name: str = _room[:-4]
                    print(_name)
                    _map = tilemap.load_tilemap(f"{self.c_src_base}/{region}/{_room}", lazy=True)
                    self._regions[region][_name] = Room(_name, region, _map)

            print("finished loading region:", region)
            return

        for _region in self._regions:
            if not DEBUG:
                print("loading:", _region)
                thread = Thread(target=load_rooms, args=(_region,))
                thread.start()
            else:
                load_rooms(_region)

    def __getitem__(self, item: Tuple[str, str]):
        return self._regions[item[0]][item[1]]

    def draw(self):
        if self._current_room:
            self._current_room.draw()

    def set_room(self, _next: Room):
        self._current_room = _next
        self._current_room.initialise()

    @property
    def current(self) -> Room:
        return self._current_room


Map: GameMap = GameMap()
