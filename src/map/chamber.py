from arcade import tilemap

# TODO: Build smarter chamber class


class Chamber:

    def __init__(self, chamber_src: str):
        self._path = chamber_src
        self._chamber_map = tilemap.load_tilemap(chamber_src)

    def draw_chamber(self):
        for sprite_list in self._chamber_map.sprite_lists.values():
            sprite_list.draw(pixelated=True)
