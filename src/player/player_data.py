from typing import Tuple, List

from arcade import Sprite


class PlayerData:

    def __init__(self, source: Sprite):
        self._source = source
        self._acceleration = (0.0, 0.0)
        self._old_position = (0.0, 0.0)

    # POSITION PROPERTIES
    @property
    def pos(self):
        return self._source.position

    @pos.setter
    def pos(self, _value: Tuple[float, float]):
        self._source.position = _value

    @property
    def x(self):
        return self._source.center_x

    @x.setter
    def x(self, _value: float):
        self._source.center_x = _value

    @property
    def y(self):
        return self._source.center_y

    @y.setter
    def y(self, _value: float):
        self._source.center_y = _value

    @property
    def bottom(self):
        return self._source.bottom

    @bottom.setter
    def bottom(self, _value: float):
        self._source.bottom = _value

    @property
    def top(self):
        return self._source.top

    @top.setter
    def top(self, _value: float):
        self._source.top = _value

    @property
    def left(self):
        return self._source.left

    @left.setter
    def left(self, _value: float):
        self._source.left = _value

    @property
    def right(self):
        return self._source.right

    @right.setter
    def right(self, _value: float):
        self._source.right = _value

    @property
    def old_pos(self):
        return self._old_position

    @old_pos.setter
    def old_pos(self, _value: Tuple[float, float]):
        self._old_position = _value

    @property
    def old_x(self):
        return self._old_position[0]

    @property
    def old_y(self):
        return self._old_position[1]

    @property
    def old_bottom(self):
        return self._old_position[1] + (self._source.bottom - self._source.center_y)

    @property
    def old_top(self):
        return self._old_position[1] + (self._source.top - self._source.center_y)

    @property
    def old_left(self):
        return self._old_position[0] + (self._source.left - self._source.center_x)

    @property
    def old_right(self):
        return self._old_position[0] + (self._source.right - self._source.center_x)

    # MOVEMENT PROPERTIES

    @property
    def vel(self):
        return self._source.velocity

    @vel.setter
    def vel(self, _value: List[float]):
        self._source.velocity = _value

    @property
    def vel_x(self):
        return self._source.change_x

    @vel_x.setter
    def vel_x(self, _value: float):
        self._source.change_x = _value

    @property
    def vel_y(self):
        return self._source.change_y

    @vel_y.setter
    def vel_y(self, _value: float):
        self._source.change_y = _value

    @property
    def acc(self):
        return self._acceleration

    @acc.setter
    def acc(self, _value: Tuple[float, float]):
        self._acceleration = _value

    @property
    def acc_x(self):
        return self._acceleration[0]

    @acc_x.setter
    def acc_x(self, _value: float):
        self._acceleration = (_value, self._acceleration[1])

    @property
    def acc_y(self):
        return self._acceleration[1]

    @acc_y.setter
    def acc_y(self, _value: float):
        self._acceleration = (self._acceleration[0], _value)

    # ANGLE PROPERTIES

    @property
    def angle(self):
        return self._source.angle

    @angle.setter
    def angle(self, _value: float):
        self._source.angle = _value

    @property
    def radians(self):
        return self._source.radians

    @radians.setter
    def radians(self, _value: float):
        self._source.radians = _value

    @property
    def vel_angle(self):
        return self._source.change_angle

    @vel_angle.setter
    def vel_angle(self, _value):
        self._source.change_angle = _value