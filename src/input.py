from typing import Dict, Set
from json import load

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

    def p_update_value(self, value: float):
        self._value = value

    @property
    def value(self):
        return self._value


class InputPoll:

    def __init__(self):
        self._buttons: Dict[str, Button] = dict()
        self._button_map: Dict[int, Button] = dict()

        self._axes_map: Dict[int, Button] = dict()
        self._axes: Dict[str, Axis] = dict()

        self._held_buttons: Set[Button] = set()

    def process_buttons(self, data_src):
        json_data = load(data_src)
        print(json_data)

    def update_buttons(self, new_map):
        raise NotImplementedError()

    def update_axes(self, new_map):
        raise NotImplementedError()

    # Key Events
    def p_key_press(self, key):
        pass

    def p_key_release(self, key):
        pass


Input = InputPoll()
