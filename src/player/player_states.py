from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from src.player.player import PlayerCharacter

from src.player.player_data import PlayerData

from src.input import Input, Button
from src.clock import Clock


class PlayerState:

    def __init__(self, _switch: "PlayerStateSwitch", _source: "PlayerCharacter", _name: str):
        self._switch: "PlayerStateSwitch" = _switch
        self._data: PlayerData = _source._data
        self._source: "PlayerCharacter" = _source
        self._hitbox = None
        self._name = _name

    def __repr__(self):
        return f"State({self._name})"

    def __str__(self):
        return self._name

    def p_into_state(self):
        raise NotImplementedError()

    def p_out_of_state(self):
        raise NotImplementedError()

    def p_update(self):
        raise NotImplementedError()

    def p_find_state(self):
        raise NotImplementedError()

    def p_jump(self, _button: Button):
        pass

    def p_crouch(self, _button: Button):
        pass

    def p_horizontal(self, _button: Button):


class StandState(PlayerState):

    def __init__(self, _switch, _source):
        super().__init__(_switch, _source, "stand")

    def p_into_state(self):
        self._data.vel_x = 0.0
        self._data.vel_y = 0.0

    def p_out_of_state(self):
        pass

    def p_update(self):
        pass

    def p_find_state(self):
        _next_state = 'stand'


class PlayerStateSwitch:

    def __init__(self, _source: "PlayerCharacter"):
        self._data: PlayerData = _source._data
        self._source: "PlayerCharacter" = _source
        self._current_state = None
        self._states: Dict[str, PlayerState] = {"stand":PlayerState(self, _source, "stand"),
                                                "walk":PlayerState(self, _source, "walk"),
                                                "run":PlayerState(self, _source, "run"),
                                                "ledge_hold":PlayerState(self, _source, "ledge_hold"),
                                                "floor_hold":PlayerState(self, _source, "floor_hold"),
                                                "jump":PlayerState(self, _source, "jump"),
                                                "fall":PlayerState(self, _source, "fall"),
                                                "slide":PlayerState(self, _source, "slide"),
                                                "wall_slide": PlayerState(self, _source, "wall_slide"),
                                                "ciel_slide": PlayerState(self, _source, "ciel_slide")}

    def find_state(self):
        _next_state: PlayerState = self._states['stand']
        if self._data.on_ground and self._data.vel_x != 0.0:
            if Input.get_button("SPRINT") and self._data.vel_x != 0.0:
                _next_state = self._states['run']
            elif Input.get_button("CROUCH") and self._data.vel_x != 0.0:
                _next_state = self._states['slide']
            else:
                _next_state = self._states['walk']
        elif self._data.vel_y > 0.0 and not self._data.on_ground:
            _next_state = self._states['jump']
        elif self._data.vel_y < 0.0 and not self._data.on_ground:
            _next_state = self._states['fall']
        elif self._data.at_ledge and ((self._data.on_left and self._data.direction == -1.0) or
                                      (self._data.on_right and self._data.direction == 1.0)):
            _next_state = self._states['ledge_hold']

        if _next_state != self._current_state:
            print(_next_state)
            self._current_state = _next_state
        # if self._current_state != _next_state:
        #     self._current_state.out_of_state()

        #     self._current_state = _next_state

        #     self._current_state.p_into_state()

        # self._current_state.p_update()

    def set_state(self, _state):
        print(_state)
        _new_state = self._states[_state]
        if _new_state != self._current_state:
            self._current_state.out_of_state()
            _new_state.p_into_state()

            self._current_state = _new_state

    @property
    def state(self):
        return self._current_state


