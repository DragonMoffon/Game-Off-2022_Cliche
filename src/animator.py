from typing import Dict, List, Tuple, Any

from json import load

from arcade import Texture, load_texture, Sprite, SpriteList
from arcade.resources import resolve_resource_path

from src.clock import Clock


def _load_from_src(_animation_src: str, _animation_name: str):
    _states: Dict[str, Dict[str, Any]] = dict()
    _frames: Dict[str, List[Dict[str, Any]]] = dict()

    _src: str = resolve_resource_path(f"{_animation_src}/{_animation_name}.json")
    _sprite_sheet_src: str = resolve_resource_path(f"{_animation_src}/{_animation_name}.png")

    with open(_src) as state_file:
        state_data = load(state_file)
        for _state in state_data['meta']['frameTags']:
            _states[_state['name']] = _state
            _frames[_state['name']] = []
            for frame in range(_state['from'], _state['to'] + 1):
                _frame_data = state_data['frames'][frame]
                _frame = load_texture(_sprite_sheet_src, x=_frame_data['frame']['x'], y=_frame_data['frame']['y'],
                                      width=_frame_data['frame']['w'], height=_frame_data['frame']['h'])

                _frames[_state['name']].append({'texture': _frame, 'duration': _frame_data['duration'],
                                                'name': _frame_data['filename']})

    return _states, _frames


class Animator:

    def __init__(self):
        self._target: Sprite = None
        self._states: Dict[str, Dict[str, Any]] = dict()
        self._frames: Dict[str, List[Dict[str, Any]]] = dict()

        self._current_frame: int = 0
        self._last_frame: float = 0.0
        self._animation_freeze: float = 0.0
        self._current_state: Dict[str, Any] = None

        self._next_state: str = ""
        self._next_frame: int = 0

    def load(self, _animation_src: str, _animation_name: str, _target: Sprite):
        self._target = _target

        self._load_states(_animation_src, _animation_name)

    def _load_states(self, _animation_src: str, _animation_name: str):
        self._states, self._frames = _load_from_src(_animation_src, _animation_name)

        self._current_state = self._states['idle']
        self._next_state = 'idle'

    def set_state(self, state: str):
        if state != self._current_state['name']:
            self._next_state = state
            if self._states[state]['priority'] >= self._current_state['priority']:
                self._current_state = self._states[state]
                self._next_frame = 0

    def animate(self):
        _frame_length = self._frames[self._current_state['name']][self._current_frame]['duration']/1000
        if Clock.length(self._last_frame) >= _frame_length:

            self._current_frame = self._next_frame

            _old_scale = self._target.scale_xy
            self._target.scale_xy = (1.0, 1.0)
            self._target.texture = self._frames[self._current_state['name']][self._current_frame]['texture']
            self._target.scale_xy = _old_scale

            self._next_frame += 1
            self._last_frame = Clock.time

            if self._next_frame >= len(self._frames[self._current_state['name']]):

                self._next_frame = 0
                self._current_state = self._states[self._next_state]

    def freeze_animation(self, _freeze_len: float):
        pass


class TempAnimator(Sprite):

    def __init__(self, x: float, y: float, dx: float, dy: float,
                 animation_data: Dict[str, Any], animation_frames: List[Dict[str, Any]],
                 loop_count: int = 1, scale_xy: Tuple[float, float] = (1.0, 1.0),):
        super().__init__()
        self.scale_xy = scale_xy

        self.position = x, y
        self.velocity = dx, dy

        self._anim_data: Dict[str, Any] = animation_data
        self._anim_frames: List[Dict[str, Any]] = animation_frames

        self._texture = self._anim_frames[0]['texture']

        self._frame = 0
        self._next_frame = 0
        self._last_frame_t = Clock.time
        self._loops = loop_count

    def update(self) -> None:
        self.position = (self.position[0] + self.velocity[0] * Clock.delta_time,
                         self.position[1] + self.velocity[1] * Clock.delta_time)

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        if Clock.length(self._last_frame_t) >= self._anim_frames[self._frame]['duration']/1000:
            self._frame = self._next_frame

            _old_scale = self.scale_xy
            self.scale_xy = (1.0, 1.0)
            self.texture = self._anim_frames[self._frame]['texture']
            self.scale_xy = _old_scale

            self._next_frame += 1
            self._last_frame_t = Clock.time

            if self._next_frame >= len(self._anim_frames):
                self._loops -= 1
                if self._loops <= 0:
                    self.remove_from_sprite_lists()
                    return
                self._next_frame = 0


class TempAnimatorManager:

    def __init__(self):
        self._animators: SpriteList = SpriteList()

        self._anims: Dict[str, Dict[str, Any]] = dict()
        self._frames: Dict[str, List[Dict[str, Any]]] = dict()

    def load(self, _animation_src: str, _animation_name: str):
        self._anims, self._frames = _load_from_src(_animation_src, _animation_name)

    def animate(self):
        for _temp in tuple(self._animators.sprite_list):
            _temp.update_animation(Clock.delta_time)

    def update(self):
        self._animators.update_animation(Clock.delta_time)

    def draw(self):
        self._animators.draw(pixelated=True)

    def add_new(self, _animation: str, x: float, y: float, dx: float = 0.0, dy: float = 0.0,
                loop_count: int = 1, scale: Tuple[float, float] = (1.0, 1.0)):
        _animator = TempAnimator(x, y, dx, dy, self._anims[_animation], self._frames[_animation],
                                 loop_count, scale)
        self._animators.append(_animator)