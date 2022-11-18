from arcade import Sprite, SpriteList


class Enemy:

    def __init__(self, _sprite: Sprite, _health: int):
        # Enemy renderer (arcade.Sprite)
        self._sprite = _sprite

        # Enemy data
        self._health: int = _health

        self._spawn_position = _sprite.position


class BoarEnemy(Enemy):

    def __init__(self, _sprite: Sprite):
        super().__init__(_sprite, 6)


class HornetEnemy(Enemy):

    def __init__(self, _sprite: Sprite):
        super().__init__(_sprite, 1)


class SnakeEnemy(Enemy):

    def __init__(self, _sprite: Sprite):
        super().__init__(_sprite, 2)


class EnemyManager:

    def __init__(self, _sprites: SpriteList):
        self._sprites = _sprites

        self._killed_enemies = []

    @property
    def sprites(self):
        return self._sprites
