from typing import Dict, Tuple

from arcade import tilemap, Sprite, SpriteList

# TODO: Build smarter chamber class


class Chamber:

    def __init__(self, chamber_src: str):
        self._path = chamber_src
        self._chamber_map = tilemap.load_tilemap(chamber_src, use_spatial_hash=True)

        # A dict of dicts with which uses cartesian coordinates to find a sprite
        self._ground_grids: Dict[str, Dict[Tuple[int, int], Sprite]] = {}
        self._decoration_layers = {}
        self._load_layers()

    def _load_layers(self):
        for layer in self._chamber_map.tiled_map.layers:
            if layer.properties.get('ground_tiles', True):
                _layer_sprites = {}
                self._ground_grids[layer.name] = _layer_sprites
                for sprite in self._chamber_map.sprite_lists[layer.name]:
                    _layer_sprites[self._chamber_map.get_cartesian(sprite.center_x, sprite.center_y)] = sprite
            else:
                pass
        _all_tiles = SpriteList(lazy=True, use_spatial_hash=True)
        _all_tiles.extend(self._chamber_map.sprite_lists['ground'])
        _all_tiles.extend(self._chamber_map.sprite_lists['one_way'])
        self._chamber_map.sprite_lists["all_ground"] = _all_tiles

    def draw_chamber(self):
        for sprite_list in self._chamber_map.sprite_lists.values():
            sprite_list.draw(pixelated=True)

    @property
    def sprite_lists(self):
        return self._chamber_map.sprite_lists

    def __getitem__(self, items: Tuple):
        if isinstance(items[0], tuple):
            _sprites = []
            for _layer in items[1:]:
                _sprite = self._ground_grids[_layer].get(items[0])
                if _sprite is not None:
                    _sprites.append(_sprite)
            return tuple(_sprites)
        else:
            pass

