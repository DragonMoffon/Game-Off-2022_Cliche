from typing import Dict, Set, Tuple
from json import load

from data.arcade_keys_str_id import Keyboard, Mouse, GameController

from src.clock import Clock


class Button:
    """
    Buttons can be pressed or held down. They can output a value from 0 to 1.
    """
    def __init__(self, _id: str):
        self._id: str = _id

        self._pressed: float = 0.0
        self._press_time: float = 0.0
        self._press_frame: int = 0

        self._press_observers: Set = set()
        self._hold_observers: Set = set()
        self._release_observers: Set = set()

    def name(self):
        return self._id

    def id(self):
        return self._id

    def __repr__(self):
        return f"{self._id} : {self._pressed}"

    def __bool__(self):
        return bool(self._pressed)

    @property
    def pressed(self):
        return self._pressed

    @property
    def press_time(self):
        return self._press_time * bool(self._pressed)

    @property
    def press_frame(self):
        return self._press_frame * bool(self._pressed)

    @property
    def release_time(self):
        return self._press_time * (not bool(self._pressed))

    @property
    def release_frame(self):
        return self._press_frame * (not bool(self._pressed))

    def held(self, length):
        return self.press_time and length >= self.press_time

    # Observable events

    def p_on_press(self, value: float = 1.0):
        if not self._pressed and value:
            self._press_time = Clock.time
            self._press_frame = Clock.frame

            self._pressed = value

            for observer_call in tuple(self._press_observers):
                observer_call(self)

    def p_on_hold(self, value: float = 1.0):
        self._pressed = value

        for observer_call in tuple(self._hold_observers):
            observer_call(self)

    def p_on_release(self):
        if self.pressed:
            self._press_time = Clock.time
            self._press_frame = Clock.frame

            self._pressed = 0.0

            for observer_call in tuple(self._release_observers):
                observer_call(self)

    # register observers
    def register_press_observer(self, observer_call):
        self._press_observers.add(observer_call)

    def register_hold_observer(self, observer_call):
        self._hold_observers.add(observer_call)

    def register_release_observer(self, observer_call):
        self._release_observers.add(observer_call)

    # de-register observers
    def deregister_press_observer(self, observer_call):
        self._press_observers.discard(observer_call)

    def deregister_hold_observer(self, observer_call):
        self._hold_observers.discard(observer_call)

    def deregister_release_observer(self, observer_call):
        self._release_observers.discard(observer_call)


class Axis:
    """
    Axis have values from -1 to 1
    """
    def __init__(self, _id: str):
        self._id: str = _id

        self._value: float = 0.0

        self._observers: set = set()

    def __repr__(self):
        return f"{self._id} : {self._value}"

    def p_update_value(self, value: float):
        self._value = max(min(self._value + value, 1.0), -1.0)

        for observer_call in tuple(self._observers):
            observer_call(self._value)

    @property
    def value(self):
        return self._value

    def register_observer(self, observer_call):
        self._observers.add(observer_call)

    # de-register observers
    def deregister_observer(self, observer_call):
        self._observers.discard(observer_call)


class InputPoll:

    def __init__(self):
        self._buttons: Dict[str, Button] = dict()  # Takes button name and returns the button object
        self._button_map: Dict[str, str] = dict()  # Takes the key name and returns the button name

        self._axes: Dict[str, Axis] = dict()  # Takes axis name and returns the axis object
        self._axes_map: Dict[str, Tuple[str, int]] = dict()  # Takes the key name and returns the axis name

        self._held_buttons: Set[Button] = set()

    def process_buttons(self, data_src):
        json_data: Dict[str, dict] = load(open(data_src))
        button_data: Dict[str, list] = json_data['Buttons']
        axis_data: dict[str, dict] = json_data['Axes']

        self._buttons = {button: Button(button) for button in button_data.keys()}
        self._button_map = {key: button for button, keys in button_data.items() for key in keys}

        self._axes = {axis: Axis(axis) for axis in axis_data.keys()}
        self._axes_map = {key: (axis, 1 if _sign == "+" else -1)
                          for axis, signs in axis_data.items() for _sign, keys in signs.items() for key in keys}

    def update_buttons(self, new_map):
        raise NotImplementedError()

    def update_axes(self, new_map):
        raise NotImplementedError()

    # Util Func
    def _key_button(self, _name):
        return _name is not None and _name in self._button_map

    def _key_axis(self, _name):
        return _name is not None and _name in self._axes_map

    # Key Events
    def p_key_held(self):
        for _button in self._held_buttons:
            _button.p_on_hold()

    def p_key_press(self, key):
        _key_name = Keyboard.key_id.get(key, None)
        if self._key_button(_key_name):
            _button = self._buttons[self._button_map[_key_name]]
            _button.p_on_press(1.0)
            self._held_buttons.add(_button)

        if self._key_axis(_key_name):
            _axis, _sign = self._axes_map[_key_name]
            self._axes[_axis].p_update_value(_sign)

    def p_key_release(self, key):
        _key_name = Keyboard.key_id.get(key, None)
        if self._key_button(_key_name):
            _button = self._buttons[self._button_map[_key_name]]
            _button.p_on_release()
            self._held_buttons.discard(_button)

        if self._key_axis(_key_name):
            _axis, _sign = self._axes_map[_key_name]
            self._axes[_axis].p_update_value(-_sign)

    def p_mouse_press(self, button):
        _button_name: str | None = Mouse.key_id.get(button, None)
        if self._key_button(_button_name):
            self._buttons[self._button_map[_button_name]].p_on_press(1.0)

        if self._key_axis(_button_name):
            _axis, _sign = self._axes_map[_button_name]
            self._axes[_axis].p_update_value(_sign)

    def p_mouse_release(self, button):
        _button_name: str | None = Mouse.key_id.get(button, None)
        if self._key_button(_button_name):
            self._buttons[self._button_map[_button_name]].p_on_release()

        if self._key_axis(_button_name):
            _axis, _sign = self._axes_map[_button_name]
            self._axes[_axis].p_update_value(-_sign)

    def p_controller_update_axis(self, axis):
        raise NotImplementedError()

    # Getters for buttons and axes
    def get_button(self, button):
        return self._buttons[button]

    def get_axis(self, axis):
        return self._axes[axis]


Input: InputPoll = InputPoll()
